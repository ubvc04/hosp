"""
Hospital Patient Portal - Authentication Module
================================================
Handles user authentication, session management, and role-based access control.
"""

from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime

from models import db, User

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize Flask-Login
login_manager = LoginManager()


def init_auth(app):
    """Initialize authentication for the Flask app."""
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Session configuration
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return User.query.get(int(user_id))


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('patient.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def patient_required(f):
    """Decorator to require patient role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.is_admin():
            return f(*args, **kwargs)
        if not current_user.is_active:
            flash('Your account has been deactivated.', 'danger')
            logout_user()
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for Admin and Patients."""
    from security import login_tracker, rate_limiter, InputValidator
    
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('patient.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        # Sanitize inputs
        email = InputValidator.sanitize_string(email, max_length=120)
        
        # Check for brute force lockout
        is_locked, remaining = login_tracker.is_locked(email)
        if is_locked:
            flash(f'Account temporarily locked. Try again in {remaining} seconds.', 'danger')
            return render_template('auth/login.html')
        
        # Also check IP-based lockout
        ip = request.remote_addr or '127.0.0.1'
        ip_locked, ip_remaining = login_tracker.is_locked(ip)
        if ip_locked:
            flash(f'Too many failed attempts. Try again in {ip_remaining} seconds.', 'danger')
            return render_template('auth/login.html')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                return render_template('auth/login.html')
            
            # Clear failed attempts on success
            login_tracker.record_success(email)
            login_tracker.record_success(ip)
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log in the user
            login_user(user, remember=bool(remember))
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            # Redirect based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('patient.dashboard'))
        else:
            # Record failed attempt
            login_tracker.record_failure(email)
            login_tracker.record_failure(ip)
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password for logged-in user."""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html')
        
        # Validate new password
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_password.html')
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('patient.dashboard'))
    
    return render_template('auth/change_password.html')


@auth_bp.route('/profile')
@login_required
def profile():
    """View user profile."""
    return render_template('auth/profile.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset via email OTP."""
    from flask import current_app, session
    from models import PasswordResetOTP
    from email_utils import send_otp_email, generate_otp
    
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address.', 'danger')
            return render_template('auth/forgot_password.html')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Clean up old OTPs for this email
            PasswordResetOTP.query.filter_by(email=email).delete()
            db.session.commit()
            
            # Generate new OTP
            otp_length = current_app.config.get('OTP_LENGTH', 6)
            otp_expiry = current_app.config.get('OTP_EXPIRY_MINUTES', 10)
            otp_code = generate_otp(otp_length)
            
            # Save OTP to database
            otp_record = PasswordResetOTP(
                email=email,
                otp_code=otp_code,
                expiry_minutes=otp_expiry
            )
            db.session.add(otp_record)
            db.session.commit()
            
            # Send OTP email
            user_name = f"{user.first_name} {user.last_name}"
            if send_otp_email(email, otp_code, user_name):
                # Store email in session for next step
                session['reset_email'] = email
                flash('OTP has been sent to your email address.', 'success')
                return redirect(url_for('auth.verify_otp'))
            else:
                flash('Failed to send OTP email. Please try again.', 'danger')
        else:
            # Don't reveal if email exists - show same message
            flash('If an account exists with this email, an OTP will be sent.', 'info')
            # Add a small delay to prevent timing attacks
            import time
            time.sleep(0.5)
    
    return render_template('auth/forgot_password.html')


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """Verify OTP code for password reset."""
    from flask import session
    from models import PasswordResetOTP
    
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Check if email is in session
    email = session.get('reset_email')
    if not email:
        flash('Please request a password reset first.', 'warning')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp', '').strip()
        
        if not otp_code:
            flash('Please enter the OTP code.', 'danger')
            return render_template('auth/verify_otp.html', email=email)
        
        # Find OTP record
        otp_record = PasswordResetOTP.query.filter_by(
            email=email,
            used=False
        ).order_by(PasswordResetOTP.created_at.desc()).first()
        
        if not otp_record:
            flash('No valid OTP found. Please request a new one.', 'danger')
            return redirect(url_for('auth.forgot_password'))
        
        # Check if OTP is expired
        if otp_record.is_expired():
            flash('OTP has expired. Please request a new one.', 'danger')
            return redirect(url_for('auth.forgot_password'))
        
        # Check max attempts (3 attempts allowed)
        if otp_record.attempts >= 3:
            otp_record.used = True
            db.session.commit()
            flash('Too many failed attempts. Please request a new OTP.', 'danger')
            return redirect(url_for('auth.forgot_password'))
        
        # Verify OTP
        if otp_record.otp_code == otp_code:
            # Mark as verified (but not used yet - used after password reset)
            session['otp_verified'] = True
            flash('OTP verified successfully! Please set your new password.', 'success')
            return redirect(url_for('auth.reset_password'))
        else:
            otp_record.increment_attempts()
            db.session.commit()
            remaining = 3 - otp_record.attempts
            flash(f'Invalid OTP. {remaining} attempts remaining.', 'danger')
    
    return render_template('auth/verify_otp.html', email=email)


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Set new password after OTP verification."""
    from flask import session
    from models import PasswordResetOTP
    from email_utils import send_password_changed_email
    
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Check if OTP was verified
    email = session.get('reset_email')
    otp_verified = session.get('otp_verified')
    
    if not email or not otp_verified:
        flash('Please complete OTP verification first.', 'warning')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate password
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/reset_password.html')
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html')
        
        # Find user and update password
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Update password
            user.set_password(new_password)
            
            # Mark OTP as used
            otp_record = PasswordResetOTP.query.filter_by(
                email=email,
                used=False
            ).first()
            if otp_record:
                otp_record.mark_used()
            
            db.session.commit()
            
            # Clear session data
            session.pop('reset_email', None)
            session.pop('otp_verified', None)
            
            # Send confirmation email
            user_name = f"{user.first_name} {user.last_name}"
            send_password_changed_email(email, user_name)
            
            flash('Password reset successful! You can now log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('auth.forgot_password'))
    
    return render_template('auth/reset_password.html')


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP code."""
    from flask import session, current_app
    from models import PasswordResetOTP
    from email_utils import send_otp_email, generate_otp
    
    email = session.get('reset_email')
    if not email:
        flash('Please request a password reset first.', 'warning')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Invalid request.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    # Clean up old OTPs
    PasswordResetOTP.query.filter_by(email=email).delete()
    db.session.commit()
    
    # Generate new OTP
    otp_length = current_app.config.get('OTP_LENGTH', 6)
    otp_expiry = current_app.config.get('OTP_EXPIRY_MINUTES', 10)
    otp_code = generate_otp(otp_length)
    
    # Save new OTP
    otp_record = PasswordResetOTP(
        email=email,
        otp_code=otp_code,
        expiry_minutes=otp_expiry
    )
    db.session.add(otp_record)
    db.session.commit()
    
    # Send OTP email
    user_name = f"{user.first_name} {user.last_name}"
    if send_otp_email(email, otp_code, user_name):
        flash('A new OTP has been sent to your email.', 'success')
    else:
        flash('Failed to send OTP. Please try again.', 'danger')
    
    return redirect(url_for('auth.verify_otp'))
