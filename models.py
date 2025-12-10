"""
Hospital Patient Portal - Database Models
==========================================
SQLAlchemy models with RSA-4096 encryption support.
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class PasswordResetOTP(db.Model):
    """OTP model for password reset functionality."""
    __tablename__ = 'password_reset_otps'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    otp_code = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)
    
    def __init__(self, email, otp_code, expiry_minutes=10):
        self.email = email
        self.otp_code = otp_code
        self.expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    
    def is_valid(self):
        """Check if OTP is still valid (not expired and not used)."""
        return not self.used and datetime.utcnow() < self.expires_at
    
    def is_expired(self):
        """Check if OTP has expired."""
        return datetime.utcnow() >= self.expires_at
    
    def mark_used(self):
        """Mark OTP as used."""
        self.used = True
    
    def increment_attempts(self):
        """Increment failed verification attempts."""
        self.attempts += 1
    
    @staticmethod
    def cleanup_expired():
        """Remove all expired OTPs from database."""
        expired = PasswordResetOTP.query.filter(
            PasswordResetOTP.expires_at < datetime.utcnow()
        ).delete()
        db.session.commit()
        return expired
    
    def __repr__(self):
        return f'<PasswordResetOTP {self.email}>'


class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='PATIENT')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationship to Patient
    patient = db.relationship('Patient', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'ADMIN'
    
    def __repr__(self):
        return f'<User {self.email}>'


class Patient(db.Model):
    """Patient information model."""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Basic Information
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)
    allergies = db.Column(db.String(500), nullable=True)
    emergency_contact = db.Column(db.String(200), nullable=True)
    
    # Encrypted Medical History (RSA-4096)
    encrypted_medical_history = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    visits = db.relationship('Visit', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    bills = db.relationship('Bill', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Patient {self.id}>'


class Visit(db.Model):
    """Medical visit records."""
    __tablename__ = 'visits'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    
    # Visit Information
    visit_date = db.Column(db.Date, nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    # Encrypted Fields (RSA-4096)
    encrypted_diagnosis = db.Column(db.Text, nullable=True)
    encrypted_prescriptions = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Visit {self.id}>'


class Bill(db.Model):
    """Billing information."""
    __tablename__ = 'bills'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    
    # Bill Information
    amount = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='unpaid')
    due_date = db.Column(db.Date, nullable=True)
    payment_date = db.Column(db.Date, nullable=True)
    
    # Encrypted Details (RSA-4096)
    encrypted_details = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Bill {self.id}: ${self.amount}>'


class Report(db.Model):
    """Medical reports (X-rays, lab reports, etc.)."""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    
    # Report Information
    report_type = db.Column(db.String(50), nullable=False)
    report_date = db.Column(db.Date, nullable=False)
    ordered_by = db.Column(db.String(100), nullable=True)
    performed_by = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    
    # File Information
    file_path = db.Column(db.String(500), nullable=True)
    
    # Encrypted Fields (RSA-4096)
    encrypted_summary = db.Column(db.Text, nullable=True)
    encrypted_findings = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Report {self.id}: {self.report_type}>'


def init_db(app):
    """Initialize database with Flask app."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
