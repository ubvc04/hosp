"""
Blockchain Routes - API endpoints for blockchain operations
===========================================================
Flask Blueprint for blockchain-related endpoints.
"""

from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from blockchain import get_blockchain, BlockchainManager
from models import db, Patient, Visit, Bill, Report
import json

blockchain_bp = Blueprint('blockchain', __name__, url_prefix='/blockchain')


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@blockchain_bp.route('/status')
@login_required
@admin_required
def status():
    """Get blockchain connection status."""
    bc = get_blockchain()
    
    status_info = {
        'connected': bc.is_connected(),
        'ganache_url': bc.ganache_url,
        'contract_deployed': bc.contract is not None,
        'contract_address': bc.contract_address
    }
    
    if bc.is_connected():
        try:
            accounts = bc.get_accounts()
            status_info['accounts'] = accounts[:5]  # First 5 accounts
            status_info['account_count'] = len(accounts)
            
            if accounts:
                status_info['primary_balance'] = str(bc.get_balance(accounts[0]))
            
            if bc.contract:
                status_info['contract_owner'] = bc.get_contract_owner()
                
        except Exception as e:
            status_info['error'] = str(e)
    
    return jsonify(status_info)


@blockchain_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Blockchain management dashboard."""
    bc = get_blockchain()
    
    context = {
        'connected': bc.is_connected(),
        'ganache_url': bc.ganache_url,
        'contract_address': bc.contract_address,
        'contract_deployed': bc.contract is not None,
        'accounts': [],
        'audit_logs': [],
        'stats': {
            'total_records': 0,
            'total_patients': 0,
            'total_audits': 0
        }
    }
    
    if bc.is_connected():
        try:
            accounts = bc.get_accounts()
            context['accounts'] = [
                {'address': acc, 'balance': str(bc.get_balance(acc))}
                for acc in accounts[:5]
            ]
            
            context['contract_owner'] = bc.get_contract_owner()
            
            # Get stats from blockchain manager
            context['stats']['total_records'] = bc.get_total_records()
            context['stats']['total_patients'] = bc.get_total_patients()
            context['stats']['total_audits'] = len(bc.get_audit_logs())
            
            # Get audit logs
            context['audit_logs'] = bc.get_audit_logs()[-20:]  # Last 20 logs
                        
        except Exception as e:
            context['error'] = str(e)
    
    return render_template('admin/blockchain_dashboard.html', **context)


@blockchain_bp.route('/store-record', methods=['POST'])
@login_required
@admin_required
def store_record():
    """Store a record hash on blockchain."""
    bc = get_blockchain()
    
    if not bc.is_connected():
        return jsonify({'error': 'Blockchain not connected'}), 503
    
    if not bc.is_connected():
        return jsonify({'error': 'Contract not deployed'}), 503
    
    data = request.get_json()
    
    patient_id = data.get('patient_id')
    record_type = data.get('record_type', 'PATIENT_INFO')
    record_data = data.get('data', {})
    
    if not patient_id:
        return jsonify({'error': 'Patient ID required'}), 400
    
    result = bc.add_record(patient_id, record_data, record_type)
    
    return jsonify(result)


@blockchain_bp.route('/verify-record', methods=['POST'])
@login_required
def verify_record():
    """Verify a record against blockchain."""
    bc = get_blockchain()
    
    if not bc.is_connected():
        return jsonify({'error': 'Blockchain not available'}), 503
    
    data = request.get_json()
    
    patient_id = data.get('patient_id')
    record_index = data.get('record_index')
    record_data = data.get('data')
    
    if not all([patient_id, record_index is not None, record_data]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    is_valid = bc.verify_record(patient_id, record_index, record_data)
    
    return jsonify({
        'verified': is_valid,
        'patient_id': patient_id,
        'record_index': record_index
    })


@blockchain_bp.route('/patient/<int:patient_id>/records')
@login_required
def get_patient_records(patient_id):
    """Get blockchain records for a patient."""
    bc = get_blockchain()
    
    # Check authorization
    if not current_user.is_admin():
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient or patient.id != patient_id:
            return jsonify({'error': 'Not authorized'}), 403
    
    if not bc.is_connected():
        return jsonify({'error': 'Blockchain not available', 'records': []}), 200
    
    records = bc.get_patient_records(patient_id)
    
    return jsonify({
        'patient_id': patient_id,
        'record_count': len(records),
        'records': records
    })


@blockchain_bp.route('/patient/<int:patient_id>/audit-logs')
@login_required
@admin_required
def get_patient_audit_logs(patient_id):
    """Get audit logs for a specific patient."""
    bc = get_blockchain()
    
    if not bc.is_connected():
        return jsonify({'error': 'Blockchain not available'}), 503
    
    logs = bc.get_audit_logs(patient_id=patient_id)
    
    return jsonify({
        'patient_id': patient_id,
        'log_count': len(logs),
        'logs': logs
    })


@blockchain_bp.route('/sync-patient/<int:patient_id>', methods=['POST'])
@login_required
@admin_required
def sync_patient_to_blockchain(patient_id):
    """Sync all patient records to blockchain."""
    bc = get_blockchain()
    
    if not bc.is_connected():
        return jsonify({'error': 'Blockchain not available'}), 503
    
    patient = Patient.query.get_or_404(patient_id)
    results = []
    
    # Store patient info
    patient_data = {
        'id': patient.id,
        'user_id': patient.user_id,
        'dob': str(patient.date_of_birth) if patient.date_of_birth else None,
        'gender': patient.gender,
        'blood_group': patient.blood_group,
        'allergies': patient.allergies,
        'created_at': str(patient.created_at)
    }
    result = bc.add_record(patient.id, patient_data, 'PATIENT_INFO')
    results.append({'type': 'PATIENT_INFO', 'result': result})
    
    # Store visits
    for visit in patient.visits:
        visit_data = {
            'id': visit.id,
            'patient_id': visit.patient_id,
            'visit_date': str(visit.visit_date),
            'doctor_name': visit.doctor_name,
            'department': visit.department,
            'notes': visit.notes,
            'created_at': str(visit.created_at)
        }
        result = bc.add_record(patient.id, visit_data, 'VISIT')
        results.append({'type': 'VISIT', 'id': visit.id, 'result': result})
    
    # Store bills
    for bill in patient.bills:
        bill_data = {
            'id': bill.id,
            'patient_id': bill.patient_id,
            'amount': str(bill.amount),
            'description': bill.description,
            'bill_date': str(bill.bill_date),
            'status': bill.status,
            'created_at': str(bill.created_at)
        }
        result = bc.add_record(patient.id, bill_data, 'BILL')
        results.append({'type': 'BILL', 'id': bill.id, 'result': result})
    
    # Store reports
    for report in patient.reports:
        report_data = {
            'id': report.id,
            'patient_id': report.patient_id,
            'report_type': report.report_type,
            'report_date': str(report.report_date),
            'doctor_name': report.doctor_name,
            'created_at': str(report.created_at)
        }
        result = bc.add_record(patient.id, report_data, 'REPORT')
        results.append({'type': 'REPORT', 'id': report.id, 'result': result})
    
    success_count = sum(1 for r in results if r.get('result', {}).get('success'))
    
    return jsonify({
        'patient_id': patient_id,
        'total_synced': len(results),
        'successful': success_count,
        'results': results
    })


@blockchain_bp.route('/sync-all', methods=['POST'])
@login_required
@admin_required
def sync_all_to_blockchain():
    """Sync all patients to blockchain."""
    bc = get_blockchain()
    
    if not bc.is_connected():
        return jsonify({'error': 'Blockchain not connected'}), 503
    
    patients = Patient.query.all()
    total_synced = 0
    patient_results = []
    
    for patient in patients:
        try:
            # Store patient info
            patient_data = {
                'id': patient.id,
                'user_id': patient.user_id,
                'dob': str(patient.date_of_birth) if patient.date_of_birth else None,
                'gender': patient.gender,
                'blood_group': patient.blood_group,
                'created_at': str(patient.created_at)
            }
            result = bc.add_record(patient.id, patient_data, 'PATIENT_INFO')
            
            if result.get('success'):
                total_synced += 1
            
            patient_results.append({
                'patient_id': patient.id,
                'success': result.get('success', False),
                'tx_hash': result.get('transaction_hash', ''),
                'error': result.get('error', '')
            })
        except Exception as e:
            patient_results.append({
                'patient_id': patient.id,
                'success': False,
                'error': str(e)
            })
    
    return jsonify({
        'total_patients': len(patients),
        'synced': total_synced,
        'results': patient_results
    })


@blockchain_bp.route('/integrity-check/<int:patient_id>')
@login_required
@admin_required
def check_integrity(patient_id):
    """Check data integrity for a patient."""
    bc = get_blockchain()
    
    if not bc.is_connected():
        return jsonify({'error': 'Blockchain not available'}), 503
    
    patient = Patient.query.get_or_404(patient_id)
    
    # Get blockchain records
    blockchain_records = bc.get_patient_records(patient_id)
    
    # Generate current hashes
    current_hashes = []
    
    # Patient info hash
    patient_data = {
        'id': patient.id,
        'user_id': patient.user_id,
        'dob': str(patient.date_of_birth) if patient.date_of_birth else None,
        'gender': patient.gender,
        'blood_group': patient.blood_group,
        'allergies': patient.allergies,
        'created_at': str(patient.created_at)
    }
    current_hashes.append({
        'type': 'PATIENT_INFO',
        'hash': bc.hash_to_hex(bc.generate_hash(patient_data))
    })
    
    integrity_status = {
        'patient_id': patient_id,
        'blockchain_records': len(blockchain_records),
        'current_records': len(current_hashes),
        'status': 'OK' if blockchain_records else 'NOT_SYNCED',
        'details': []
    }
    
    # Check if any hashes match (simplified check)
    for bc_record in blockchain_records:
        matched = False
        for curr in current_hashes:
            if bc_record['hash'] == curr['hash']:
                matched = True
                break
        
        integrity_status['details'].append({
            'blockchain_hash': bc_record['hash'],
            'type': bc_record['record_type'],
            'timestamp': bc_record['timestamp'],
            'verified': matched
        })
    
    return jsonify(integrity_status)
