"""
Hospital Patient Portal - Admin Routes
======================================
All admin functionality for managing patients, visits, bills, and reports.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from models import db, User, Patient, Visit, Bill, Report
from crypto_utils import get_crypto

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to restrict access to admin users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# ============== DASHBOARD ==============

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with overview statistics."""
    total_patients = Patient.query.count()
    total_visits = Visit.query.count()
    total_bills = Bill.query.count()
    pending_bills = Bill.query.filter_by(status='unpaid').count()
    
    # Recent patients
    recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
    
    # Recent visits
    recent_visits = Visit.query.order_by(Visit.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
        total_patients=total_patients,
        total_visits=total_visits,
        total_bills=total_bills,
        pending_bills=pending_bills,
        recent_patients=recent_patients,
        recent_visits=recent_visits
    )


# ============== PATIENTS ==============

@admin_bp.route('/patients')
@login_required
@admin_required
def patients_list():
    """List all patients."""
    search = request.args.get('search', '')
    
    query = Patient.query.join(User)
    if search:
        query = query.filter(
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    patients = query.order_by(Patient.created_at.desc()).all()
    return render_template('admin/patients_list.html', patients=patients, search=search)


@admin_bp.route('/patients/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_patient():
    """Add a new patient."""
    if request.method == 'POST':
        try:
            crypto = get_crypto()
            
            # Create user account
            user = User(
                email=request.form['email'],
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                phone=request.form.get('phone'),
                role='PATIENT'
            )
            user.set_password(request.form.get('password') or 'Patient@123')
            db.session.add(user)
            db.session.flush()
            
            # Get health condition
            health_condition = request.form.get('health_condition', '')
            if health_condition == 'Other':
                health_condition = request.form.get('other_condition', 'Other')
            
            # Create patient record
            patient = Patient(
                user_id=user.id,
                date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date() if request.form.get('date_of_birth') else None,
                gender=request.form.get('gender'),
                blood_group=request.form.get('blood_group'),
                allergies=health_condition,  # Using allergies field to store health condition
                emergency_contact=request.form.get('emergency_contact'),
                encrypted_medical_history=crypto.encrypt(request.form.get('medical_history', '')) if request.form.get('medical_history') else None
            )
            db.session.add(patient)
            db.session.flush()
            
            # Handle file uploads
            upload_folder = current_app.config['UPLOAD_FOLDER']
            patient_folder = os.path.join(upload_folder, f'patient_{patient.id}')
            os.makedirs(patient_folder, exist_ok=True)
            
            # Define document types and their form field names
            doc_types = {
                'medical_bills': 'Medical Bills',
                'op_reports': 'OP Reports',
                'scan_reports': 'Scan Reports',
                'lab_reports': 'Lab Reports',
                'prescriptions': 'Prescriptions',
                'discharge_summary': 'Discharge Summary',
                'insurance_docs': 'Insurance Documents',
                'other_docs': 'Other Documents'
            }
            
            uploaded_files = []
            for field_name, doc_type in doc_types.items():
                files = request.files.getlist(field_name)
                for file in files:
                    if file and file.filename:
                        # Secure the filename
                        from werkzeug.utils import secure_filename
                        filename = secure_filename(file.filename)
                        # Add timestamp to avoid conflicts
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        new_filename = f"{field_name}_{timestamp}_{filename}"
                        filepath = os.path.join(patient_folder, new_filename)
                        file.save(filepath)
                        
                        # Create report entry for each uploaded file
                        report = Report(
                            patient_id=patient.id,
                            report_type=doc_type,
                            report_date=datetime.now().date(),
                            ordered_by='Initial Upload',
                            status='completed',
                            file_path=filepath
                        )
                        db.session.add(report)
                        uploaded_files.append(filename)
            
            db.session.commit()
            
            success_msg = f'Patient {user.first_name} {user.last_name} added successfully!'
            if uploaded_files:
                success_msg += f' {len(uploaded_files)} document(s) uploaded.'
            flash(success_msg, 'success')
            return redirect(url_for('admin.view_patient', patient_id=patient.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding patient: {str(e)}', 'danger')
    
    return render_template('admin/add_patient.html')


@admin_bp.route('/patients/<int:patient_id>')
@login_required
@admin_required
def view_patient(patient_id):
    """View patient details."""
    patient = Patient.query.get_or_404(patient_id)
    crypto = get_crypto()
    
    # Decrypt medical history
    medical_history = crypto.decrypt(patient.encrypted_medical_history) if patient.encrypted_medical_history else ''
    
    # Get visits with decrypted data
    visits = []
    for visit in patient.visits.order_by(Visit.visit_date.desc()).all():
        visits.append({
            'id': visit.id,
            'visit_date': visit.visit_date,
            'doctor_name': visit.doctor_name,
            'department': visit.department,
            'diagnosis': crypto.decrypt(visit.encrypted_diagnosis) if visit.encrypted_diagnosis else '',
            'prescriptions': crypto.decrypt(visit.encrypted_prescriptions) if visit.encrypted_prescriptions else '',
            'notes': visit.notes
        })
    
    # Get bills with decrypted data
    bills = []
    for bill in patient.bills.order_by(Bill.created_at.desc()).all():
        bills.append({
            'id': bill.id,
            'amount': bill.amount,
            'description': bill.description,
            'status': bill.status,
            'due_date': bill.due_date,
            'details': crypto.decrypt(bill.encrypted_details) if bill.encrypted_details else ''
        })
    
    # Get reports with decrypted data
    reports = []
    for report in patient.reports.order_by(Report.report_date.desc()).all():
        reports.append({
            'id': report.id,
            'report_type': report.report_type,
            'report_date': report.report_date,
            'ordered_by': report.ordered_by,
            'performed_by': report.performed_by,
            'status': report.status,
            'summary': crypto.decrypt(report.encrypted_summary) if report.encrypted_summary else '',
            'findings': crypto.decrypt(report.encrypted_findings) if report.encrypted_findings else ''
        })
    
    return render_template('admin/view_patient.html',
        patient=patient,
        medical_history=medical_history,
        visits=visits,
        bills=bills,
        reports=reports
    )


@admin_bp.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_patient(patient_id):
    """Edit patient details."""
    patient = Patient.query.get_or_404(patient_id)
    crypto = get_crypto()
    
    if request.method == 'POST':
        try:
            # Update user info
            patient.user.first_name = request.form['first_name']
            patient.user.last_name = request.form['last_name']
            patient.user.email = request.form['email']
            patient.user.phone = request.form.get('phone')
            
            # Update patient info
            if request.form.get('date_of_birth'):
                patient.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            patient.gender = request.form.get('gender')
            patient.blood_group = request.form.get('blood_group')
            patient.allergies = request.form.get('allergies')
            patient.emergency_contact = request.form.get('emergency_contact')
            
            if request.form.get('medical_history'):
                patient.encrypted_medical_history = crypto.encrypt(request.form['medical_history'])
            
            db.session.commit()
            flash('Patient updated successfully!', 'success')
            return redirect(url_for('admin.view_patient', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating patient: {str(e)}', 'danger')
    
    # Decrypt for editing
    medical_history = crypto.decrypt(patient.encrypted_medical_history) if patient.encrypted_medical_history else ''
    
    return render_template('admin/edit_patient.html', patient=patient, medical_history=medical_history)


@admin_bp.route('/patients/<int:patient_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_patient(patient_id):
    """Delete a patient."""
    patient = Patient.query.get_or_404(patient_id)
    user = patient.user
    
    try:
        db.session.delete(patient)
        db.session.delete(user)
        db.session.commit()
        flash('Patient deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting patient: {str(e)}', 'danger')
    
    return redirect(url_for('admin.patients_list'))


# ============== VISITS ==============

@admin_bp.route('/visits')
@login_required
@admin_required
def visits_list():
    """List all visits."""
    visits = Visit.query.order_by(Visit.visit_date.desc()).all()
    return render_template('admin/visits_list.html', visits=visits)


@admin_bp.route('/visits/add', methods=['GET', 'POST'])
@admin_bp.route('/visits/add/<int:patient_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def add_visit(patient_id=None):
    """Add a new visit."""
    if request.method == 'POST':
        try:
            crypto = get_crypto()
            patient_id = int(request.form['patient_id'])
            
            # Verify patient exists
            patient = Patient.query.get_or_404(patient_id)
            
            visit = Visit(
                patient_id=patient_id,
                visit_date=datetime.strptime(request.form['visit_date'], '%Y-%m-%d').date(),
                doctor_name=request.form['doctor_name'],
                department=request.form['department'],
                notes=request.form.get('notes'),
                encrypted_diagnosis=crypto.encrypt(request.form['diagnosis']) if request.form.get('diagnosis') else None,
                encrypted_prescriptions=crypto.encrypt(request.form['prescriptions']) if request.form.get('prescriptions') else None
            )
            
            db.session.add(visit)
            db.session.commit()
            
            flash('Visit added successfully!', 'success')
            return redirect(url_for('admin.view_patient', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding visit: {str(e)}', 'danger')
    
    patients = Patient.query.all()
    return render_template('admin/add_visit.html', patient_id=patient_id, patients=patients)


# ============== BILLS ==============

@admin_bp.route('/bills')
@login_required
@admin_required
def bills_list():
    """List all bills."""
    status_filter = request.args.get('status', '')
    
    query = Bill.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    bills = query.order_by(Bill.created_at.desc()).all()
    return render_template('admin/bills_list.html', bills=bills, current_filter=status_filter)


@admin_bp.route('/bills/add', methods=['GET', 'POST'])
@admin_bp.route('/bills/add/<int:patient_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def add_bill(patient_id=None):
    """Add a new bill."""
    if request.method == 'POST':
        try:
            crypto = get_crypto()
            patient_id = int(request.form['patient_id'])
            
            # Verify patient exists
            patient = Patient.query.get_or_404(patient_id)
            
            bill = Bill(
                patient_id=patient_id,
                amount=float(request.form['amount']),
                description=request.form.get('description'),
                status=request.form.get('status', 'unpaid'),
                due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d').date() if request.form.get('due_date') else None,
                encrypted_details=crypto.encrypt(request.form['details']) if request.form.get('details') else None
            )
            
            db.session.add(bill)
            db.session.commit()
            
            flash('Bill created successfully!', 'success')
            return redirect(url_for('admin.view_patient', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating bill: {str(e)}', 'danger')
    
    patients = Patient.query.all()
    return render_template('admin/add_bill.html', patient_id=patient_id, patients=patients)


@admin_bp.route('/bills/<int:bill_id>/update', methods=['POST'])
@login_required
@admin_required
def update_bill(bill_id):
    """Update bill status."""
    bill = Bill.query.get_or_404(bill_id)
    
    new_status = request.form.get('status')
    if new_status:
        bill.status = new_status
        if new_status == 'paid':
            bill.payment_date = datetime.utcnow().date()
        db.session.commit()
        flash('Bill updated successfully!', 'success')
    
    return redirect(url_for('admin.view_patient', patient_id=bill.patient_id))


# ============== REPORTS ==============

@admin_bp.route('/reports')
@login_required
@admin_required
def reports_list():
    """List all reports."""
    reports = Report.query.order_by(Report.report_date.desc()).all()
    return render_template('admin/reports_list.html', reports=reports)


@admin_bp.route('/reports/add', methods=['GET', 'POST'])
@admin_bp.route('/reports/add/<int:patient_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def add_report(patient_id=None):
    """Add a new report."""
    if request.method == 'POST':
        try:
            crypto = get_crypto()
            patient_id = int(request.form['patient_id'])
            
            # Verify patient exists
            patient = Patient.query.get_or_404(patient_id)
            
            # Handle file upload
            file_path = None
            if 'report_file' in request.files:
                file = request.files['report_file']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_name = f"{patient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, file_name)
                    file.save(file_path)
            
            report = Report(
                patient_id=patient_id,
                report_type=request.form['report_type'],
                report_date=datetime.strptime(request.form['report_date'], '%Y-%m-%d').date(),
                ordered_by=request.form.get('ordered_by'),
                performed_by=request.form.get('performed_by'),
                status=request.form.get('status', 'pending'),
                file_path=file_path,
                encrypted_summary=crypto.encrypt(request.form['summary']) if request.form.get('summary') else None,
                encrypted_findings=crypto.encrypt(request.form['findings']) if request.form.get('findings') else None
            )
            
            db.session.add(report)
            db.session.commit()
            
            flash('Report added successfully!', 'success')
            return redirect(url_for('admin.view_patient', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding report: {str(e)}', 'danger')
    
    patients = Patient.query.all()
    return render_template('admin/add_report.html', patient_id=patient_id, patients=patients)


@admin_bp.route('/reports/<int:report_id>')
@login_required
@admin_required
def view_report(report_id):
    """View report details."""
    report = Report.query.get_or_404(report_id)
    crypto = get_crypto()
    
    report_summary = crypto.decrypt(report.encrypted_summary) if report.encrypted_summary else ''
    findings = crypto.decrypt(report.encrypted_findings) if report.encrypted_findings else ''
    
    return render_template('admin/view_report.html',
        report=report,
        report_summary=report_summary,
        findings=findings
    )


@admin_bp.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_report(report_id):
    """Delete a report."""
    report = Report.query.get_or_404(report_id)
    patient_id = report.patient_id
    
    try:
        # Delete file if exists
        if report.file_path and os.path.exists(report.file_path):
            os.remove(report.file_path)
        
        db.session.delete(report)
        db.session.commit()
        flash('Report deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting report: {str(e)}', 'danger')
    
    return redirect(url_for('admin.view_patient', patient_id=patient_id))


@admin_bp.route('/reports/<int:report_id>/status', methods=['POST'])
@login_required
@admin_required
def update_report_status(report_id):
    """Update report status."""
    report = Report.query.get_or_404(report_id)
    
    new_status = request.form.get('status')
    if new_status:
        report.status = new_status
        db.session.commit()
        flash('Report status updated!', 'success')
    
    return redirect(url_for('admin.view_report', report_id=report_id))


# ============== DATABASE MANAGEMENT ==============

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Admin settings page with database management."""
    # Get database stats
    total_patients = Patient.query.count()
    total_visits = Visit.query.count()
    total_bills = Bill.query.count()
    total_reports = Report.query.count()
    total_users = User.query.count()
    
    return render_template('admin/settings.html',
        total_patients=total_patients,
        total_visits=total_visits,
        total_bills=total_bills,
        total_reports=total_reports,
        total_users=total_users
    )


@admin_bp.route('/reset-database', methods=['POST'])
@login_required
@admin_required
def reset_database():
    """Reset the database - delete all patient data but keep admin."""
    confirmation = request.form.get('confirmation', '')
    
    if confirmation != 'RESET':
        flash('Invalid confirmation. Database reset cancelled.', 'danger')
        return redirect(url_for('admin.settings'))
    
    try:
        # Delete all data in order (respecting foreign keys)
        Report.query.delete()
        Bill.query.delete()
        Visit.query.delete()
        Patient.query.delete()
        
        # Delete all patient users (keep admin)
        User.query.filter_by(role='PATIENT').delete()
        
        db.session.commit()
        
        flash('Database reset successful! All patient data has been deleted.', 'success')
        current_app.logger.info(f'Database reset by admin: {current_user.email}')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting database: {str(e)}', 'danger')
        current_app.logger.error(f'Database reset failed: {str(e)}')
    
    return redirect(url_for('admin.settings'))


@admin_bp.route('/clear-visits', methods=['POST'])
@login_required
@admin_required
def clear_visits():
    """Clear all visits data."""
    try:
        Visit.query.delete()
        db.session.commit()
        flash('All visits have been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing visits: {str(e)}', 'danger')
    
    return redirect(url_for('admin.settings'))


@admin_bp.route('/clear-bills', methods=['POST'])
@login_required
@admin_required
def clear_bills():
    """Clear all bills data."""
    try:
        Bill.query.delete()
        db.session.commit()
        flash('All bills have been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing bills: {str(e)}', 'danger')
    
    return redirect(url_for('admin.settings'))


@admin_bp.route('/clear-reports', methods=['POST'])
@login_required
@admin_required
def clear_reports():
    """Clear all reports data."""
    try:
        Report.query.delete()
        db.session.commit()
        flash('All reports have been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing reports: {str(e)}', 'danger')
    
    return redirect(url_for('admin.settings'))
