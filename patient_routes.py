"""
Hospital Patient Portal - Patient Routes
========================================
Patient-specific routes for viewing their own records.
"""

import os
from flask import Blueprint, render_template, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

from models import db, Patient, Visit, Bill, Report
from crypto_utils import get_crypto
from ai_suggestions import get_suggestion_engine

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')


def patient_required(f):
    """Decorator to restrict access to patient users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.is_admin():
            flash('This area is for patients only.', 'warning')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_patient():
    """Get the current logged-in patient's record."""
    if current_user.is_admin():
        return None
    return Patient.query.filter_by(user_id=current_user.id).first()


# ============== DASHBOARD ==============

@patient_bp.route('/dashboard')
@login_required
@patient_required
def dashboard():
    """Patient dashboard with overview and AI suggestions."""
    patient = get_current_patient()
    
    if not patient:
        flash('Patient record not found. Please contact the administrator.', 'danger')
        return redirect(url_for('auth.logout'))
    
    crypto = get_crypto()
    
    # Get visits
    visits = patient.visits.order_by(Visit.visit_date.desc()).all()
    
    # Decrypt visit data for display
    decrypted_visits = []
    for visit in visits:
        decrypted_visits.append({
            'id': visit.id,
            'visit_date': visit.visit_date,
            'doctor_name': visit.doctor_name,
            'department': visit.department,
            'decrypted_diagnosis': crypto.decrypt(visit.encrypted_diagnosis) if visit.encrypted_diagnosis else '',
            'decrypted_prescriptions': crypto.decrypt(visit.encrypted_prescriptions) if visit.encrypted_prescriptions else '',
            'notes': visit.notes
        })
    
    # Get bills
    bills = patient.bills.order_by(Bill.created_at.desc()).all()
    pending_bills = sum(1 for b in bills if b.status == 'unpaid')
    
    # Get reports
    reports = patient.reports.order_by(Report.report_date.desc()).all()
    
    # Calculate age for AI suggestions
    age = None
    if patient.date_of_birth:
        today = datetime.today()
        age = today.year - patient.date_of_birth.year - (
            (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
        )
    
    # Get AI suggestions
    suggestion_engine = get_suggestion_engine()
    medical_history = crypto.decrypt(patient.encrypted_medical_history) if patient.encrypted_medical_history else ''
    
    ai_suggestions = suggestion_engine.get_suggestions(
        age=age,
        gender=patient.gender,
        visit_count=len(visits),
        medical_history=medical_history
    )
    
    return render_template('patient/dashboard.html',
        patient=patient,
        visits=decrypted_visits,
        bills=bills,
        reports=reports,
        pending_bills=pending_bills,
        ai_suggestions=ai_suggestions
    )


# ============== RECORDS ==============

@patient_bp.route('/records')
@login_required
@patient_required
def my_records():
    """View medical records."""
    patient = get_current_patient()
    
    if not patient:
        flash('Patient record not found.', 'danger')
        return redirect(url_for('patient.dashboard'))
    
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
            'decrypted_diagnosis': crypto.decrypt(visit.encrypted_diagnosis) if visit.encrypted_diagnosis else '',
            'decrypted_prescriptions': crypto.decrypt(visit.encrypted_prescriptions) if visit.encrypted_prescriptions else '',
            'notes': visit.notes
        })
    
    return render_template('patient/records.html',
        patient=patient,
        medical_history=medical_history,
        visits=visits
    )


# ============== BILLS ==============

@patient_bp.route('/bills')
@login_required
@patient_required
def my_bills():
    """View billing history."""
    patient = get_current_patient()
    
    if not patient:
        flash('Patient record not found.', 'danger')
        return redirect(url_for('patient.dashboard'))
    
    crypto = get_crypto()
    
    # Get bills with decrypted details
    bills = []
    for bill in patient.bills.order_by(Bill.created_at.desc()).all():
        bills.append({
            'id': bill.id,
            'amount': bill.amount,
            'description': bill.description,
            'status': bill.status,
            'due_date': bill.due_date,
            'payment_date': bill.payment_date,
            'created_at': bill.created_at,
            'decrypted_details': crypto.decrypt(bill.encrypted_details) if bill.encrypted_details else ''
        })
    
    return render_template('patient/bills.html', patient=patient, bills=bills)


# ============== REPORTS ==============

@patient_bp.route('/reports')
@login_required
@patient_required
def my_reports():
    """View medical reports."""
    patient = get_current_patient()
    
    if not patient:
        flash('Patient record not found.', 'danger')
        return redirect(url_for('patient.dashboard'))
    
    crypto = get_crypto()
    
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
            'file_path': report.file_path,
            'decrypted_summary': crypto.decrypt(report.encrypted_summary) if report.encrypted_summary else '',
            'decrypted_findings': crypto.decrypt(report.encrypted_findings) if report.encrypted_findings else ''
        })
    
    return render_template('patient/reports.html', patient=patient, reports=reports)


@patient_bp.route('/reports/<int:report_id>/download')
@login_required
@patient_required
def download_report(report_id):
    """Download a report file."""
    patient = get_current_patient()
    
    if not patient:
        flash('Patient record not found.', 'danger')
        return redirect(url_for('patient.dashboard'))
    
    report = Report.query.get_or_404(report_id)
    
    # Verify patient owns this report
    if report.patient_id != patient.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('patient.my_reports'))
    
    if not report.file_path or not os.path.exists(report.file_path):
        flash('Report file not found.', 'warning')
        return redirect(url_for('patient.my_reports'))
    
    return send_file(report.file_path, as_attachment=True)
