"""
Hospital Patient Portal - Forms Module
======================================
WTForms definitions for secure form handling with validation.

SECURITY FEATURES:
-----------------
- CSRF protection enabled on all forms
- Server-side validation
- Input sanitization
- Length and format validation
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, TextAreaField,
    IntegerField, FloatField, DateField, BooleanField, HiddenField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Optional,
    NumberRange, ValidationError, Regexp
)
from datetime import date


class LoginForm(FlaskForm):
    """
    Login form for both Admin and Patient users.
    
    CSRF protection is automatic with Flask-WTF.
    """
    username = StringField('Username / Patient ID', validators=[
        DataRequired(message="Username is required"),
        Length(min=3, max=80, message="Username must be between 3 and 80 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=6, max=128, message="Password must be between 6 and 128 characters")
    ])
    remember_me = BooleanField('Remember Me')


class ChangePasswordForm(FlaskForm):
    """Form for changing password."""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message="Current password is required")
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message="New password is required"),
        Length(min=8, max=128, message="Password must be at least 8 characters"),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
            message="Password must contain at least one uppercase letter, one lowercase letter, and one number"
        )
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('new_password', message="Passwords must match")
    ])


class PatientForm(FlaskForm):
    """
    Form for creating/editing patient records.
    
    Admin only - used to add or update patient information.
    """
    # Basic Information
    name = StringField('Full Name', validators=[
        DataRequired(message="Name is required"),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters")
    ])
    
    age = IntegerField('Age', validators=[
        DataRequired(message="Age is required"),
        NumberRange(min=0, max=150, message="Please enter a valid age")
    ])
    
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], validators=[DataRequired(message="Gender is required")])
    
    contact = StringField('Contact Number', validators=[
        DataRequired(message="Contact number is required"),
        Length(min=10, max=20, message="Please enter a valid contact number"),
        Regexp(r'^\+?[\d\s\-()]+$', message="Please enter a valid phone number")
    ])
    
    email = StringField('Email', validators=[
        Optional(),
        Email(message="Please enter a valid email address")
    ])
    
    address = TextAreaField('Address', validators=[
        Optional(),
        Length(max=500, message="Address must be less than 500 characters")
    ])
    
    # Patient Category
    category = SelectField('Patient Category', choices=[
        ('OUT_PATIENT', 'Out-Patient'),
        ('IN_PATIENT', 'In-Patient')
    ], validators=[DataRequired()])
    
    # Admission Details (for in-patients)
    room_number = StringField('Room Number', validators=[
        Optional(),
        Length(max=20)
    ])
    
    admission_date = DateField('Admission Date', validators=[Optional()])
    
    # Medical Information (will be encrypted)
    medical_history = TextAreaField('Medical History', validators=[
        Optional(),
        Length(max=5000, message="Medical history must be less than 5000 characters")
    ])
    
    diagnosis = TextAreaField('Current Diagnosis', validators=[
        Optional(),
        Length(max=2000, message="Diagnosis must be less than 2000 characters")
    ])
    
    prescriptions = TextAreaField('Current Prescriptions', validators=[
        Optional(),
        Length(max=2000, message="Prescriptions must be less than 2000 characters")
    ])
    
    other_details = TextAreaField('Other Medical Details', validators=[
        Optional(),
        Length(max=2000)
    ])
    
    # Account Settings
    initial_password = PasswordField('Initial Password (for patient login)', validators=[
        Optional(),
        Length(min=6, max=128, message="Password must be at least 6 characters")
    ])
    
    status = SelectField('Account Status', choices=[
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    ], default='ACTIVE')


class VisitForm(FlaskForm):
    """Form for recording patient visits."""
    patient_id = StringField('Patient ID', validators=[
        DataRequired(message="Patient ID is required")
    ])
    
    visit_date = DateField('Visit Date', validators=[
        DataRequired(message="Visit date is required")
    ], default=date.today)
    
    visit_type = SelectField('Visit Type', choices=[
        ('CHECKUP', 'Regular Checkup'),
        ('EMERGENCY', 'Emergency'),
        ('FOLLOW_UP', 'Follow-up'),
        ('CONSULTATION', 'Consultation'),
        ('PROCEDURE', 'Procedure'),
        ('OTHER', 'Other')
    ], validators=[DataRequired()])
    
    doctor_name = StringField('Doctor Name', validators=[
        DataRequired(message="Doctor name is required"),
        Length(min=2, max=100)
    ])
    
    department = SelectField('Department', choices=[
        ('General Medicine', 'General Medicine'),
        ('Cardiology', 'Cardiology'),
        ('Orthopedics', 'Orthopedics'),
        ('Pediatrics', 'Pediatrics'),
        ('Gynecology', 'Gynecology'),
        ('Neurology', 'Neurology'),
        ('Dermatology', 'Dermatology'),
        ('ENT', 'ENT'),
        ('Ophthalmology', 'Ophthalmology'),
        ('Psychiatry', 'Psychiatry'),
        ('Surgery', 'Surgery'),
        ('Emergency', 'Emergency'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    
    # Encrypted fields
    symptoms = TextAreaField('Symptoms', validators=[
        Optional(),
        Length(max=2000)
    ])
    
    visit_details = TextAreaField('Visit Details / Notes', validators=[
        Optional(),
        Length(max=5000)
    ])
    
    treatment = TextAreaField('Treatment / Recommendations', validators=[
        Optional(),
        Length(max=2000)
    ])


class BillForm(FlaskForm):
    """Form for creating/editing bills."""
    patient_id = StringField('Patient ID', validators=[
        DataRequired(message="Patient ID is required")
    ])
    
    bill_date = DateField('Bill Date', validators=[
        DataRequired(message="Bill date is required")
    ], default=date.today)
    
    due_date = DateField('Due Date', validators=[Optional()])
    
    amount = FloatField('Total Amount ($)', validators=[
        DataRequired(message="Amount is required"),
        NumberRange(min=0, message="Amount must be positive")
    ])
    
    paid_amount = FloatField('Paid Amount ($)', validators=[
        Optional(),
        NumberRange(min=0, message="Paid amount must be positive")
    ], default=0.0)
    
    # Encrypted field
    bill_details = TextAreaField('Bill Details (Itemized)', validators=[
        Optional(),
        Length(max=5000)
    ])
    
    status = SelectField('Payment Status', choices=[
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid')
    ], default='UNPAID')


class ReportForm(FlaskForm):
    """Form for adding medical reports."""
    patient_id = StringField('Patient ID', validators=[
        DataRequired(message="Patient ID is required")
    ])
    
    report_type = SelectField('Report Type', choices=[
        ('X_RAY', 'X-Ray'),
        ('MRI', 'MRI'),
        ('CT_SCAN', 'CT Scan'),
        ('ULTRASOUND', 'Ultrasound'),
        ('LAB_REPORT', 'Lab Report'),
        ('BLOOD_TEST', 'Blood Test'),
        ('URINE_TEST', 'Urine Test'),
        ('ECG', 'ECG'),
        ('ECHO', 'Echocardiogram'),
        ('OTHER', 'Other')
    ], validators=[DataRequired()])
    
    report_date = DateField('Report Date', validators=[
        DataRequired(message="Report date is required")
    ], default=date.today)
    
    ordered_by = StringField('Ordered By (Doctor)', validators=[
        Optional(),
        Length(max=100)
    ])
    
    performed_by = StringField('Performed By', validators=[
        Optional(),
        Length(max=100)
    ])
    
    # Encrypted fields
    report_summary = TextAreaField('Report Summary', validators=[
        Optional(),
        Length(max=5000)
    ])
    
    findings = TextAreaField('Findings / Results', validators=[
        Optional(),
        Length(max=5000)
    ])
    
    status = SelectField('Status', choices=[
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed')
    ], default='COMPLETED')


class SearchForm(FlaskForm):
    """Form for searching patients."""
    query = StringField('Search', validators=[
        Optional(),
        Length(max=100)
    ])
    
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('IN_PATIENT', 'In-Patient'),
        ('OUT_PATIENT', 'Out-Patient')
    ])
    
    status = SelectField('Status', choices=[
        ('', 'All Status'),
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    ])
