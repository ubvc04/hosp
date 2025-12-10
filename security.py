"""
Hospital Patient Portal - Security Module
==========================================
Advanced security features including rate limiting, input validation,
security logging, and attack detection.
"""

import re
import time
import hashlib
import logging
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta
from flask import request, jsonify, abort, g

# Configure security logger
security_logger = logging.getLogger('security')
handler = logging.FileHandler('security.log')
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
security_logger.addHandler(handler)
security_logger.setLevel(logging.WARNING)


class RateLimiter:
    """
    In-memory rate limiter with sliding window algorithm.
    For production, use Redis-based rate limiting.
    """
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = {}
    
    def _get_client_ip(self):
        """Get the real client IP address."""
        # Check for proxy headers
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        return request.remote_addr or '127.0.0.1'
    
    def _cleanup_old_requests(self, ip, window_seconds):
        """Remove requests outside the time window."""
        cutoff = time.time() - window_seconds
        self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]
    
    def is_blocked(self, ip):
        """Check if an IP is temporarily blocked."""
        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]:
                return True
            else:
                del self.blocked_ips[ip]
        return False
    
    def block_ip(self, ip, duration_seconds=300):
        """Block an IP for a specified duration."""
        self.blocked_ips[ip] = time.time() + duration_seconds
        security_logger.warning(f"IP {ip} blocked for {duration_seconds} seconds")
    
    def check_rate_limit(self, max_requests, window_seconds):
        """
        Check if the current request exceeds rate limit.
        
        Args:
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            Tuple of (is_limited, remaining, reset_time)
        """
        ip = self._get_client_ip()
        
        # Check if IP is blocked
        if self.is_blocked(ip):
            return True, 0, int(self.blocked_ips[ip] - time.time())
        
        # Clean up old requests
        self._cleanup_old_requests(ip, window_seconds)
        
        # Check rate limit
        current_count = len(self.requests[ip])
        
        if current_count >= max_requests:
            # Auto-block if significantly over limit
            if current_count >= max_requests * 3:
                self.block_ip(ip, 300)  # Block for 5 minutes
            
            reset_time = window_seconds - (time.time() - self.requests[ip][0])
            return True, 0, int(reset_time)
        
        # Record this request
        self.requests[ip].append(time.time())
        
        remaining = max_requests - len(self.requests[ip])
        return False, remaining, window_seconds


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests=60, window_seconds=60):
    """
    Decorator to apply rate limiting to a route.
    
    Args:
        max_requests: Maximum requests allowed per window
        window_seconds: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            is_limited, remaining, reset_time = rate_limiter.check_rate_limit(
                max_requests, window_seconds
            )
            
            # Add rate limit headers
            g.rate_limit_remaining = remaining
            g.rate_limit_reset = reset_time
            
            if is_limited:
                security_logger.warning(
                    f"Rate limit exceeded for {rate_limiter._get_client_ip()} "
                    f"on {request.path}"
                )
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': reset_time
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class InputValidator:
    """
    Input validation and sanitization utilities.
    """
    
    # Patterns for common attack vectors
    SQL_INJECTION_PATTERN = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)|"
        r"(--|;|'|\"|\x00|\\x00)",
        re.IGNORECASE
    )
    
    XSS_PATTERN = re.compile(
        r"(<script|javascript:|on\w+\s*=|<iframe|<object|<embed|<form)",
        re.IGNORECASE
    )
    
    PATH_TRAVERSAL_PATTERN = re.compile(
        r"(\.\./|\.\.\\|%2e%2e|%252e%252e)",
        re.IGNORECASE
    )
    
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    PHONE_PATTERN = re.compile(
        r'^[\d\s\-\+\(\)]{10,20}$'
    )
    
    @classmethod
    def sanitize_string(cls, value, max_length=500):
        """
        Sanitize a string input.
        
        Args:
            value: Input string
            max_length: Maximum allowed length
        
        Returns:
            Sanitized string
        """
        if not value:
            return ''
        
        # Convert to string and strip
        value = str(value).strip()
        
        # Truncate to max length
        value = value[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        return value
    
    @classmethod
    def check_sql_injection(cls, value):
        """Check for potential SQL injection patterns."""
        if cls.SQL_INJECTION_PATTERN.search(str(value)):
            security_logger.warning(
                f"Potential SQL injection detected: {value[:100]}"
            )
            return True
        return False
    
    @classmethod
    def check_xss(cls, value):
        """Check for potential XSS patterns."""
        if cls.XSS_PATTERN.search(str(value)):
            security_logger.warning(
                f"Potential XSS detected: {value[:100]}"
            )
            return True
        return False
    
    @classmethod
    def check_path_traversal(cls, value):
        """Check for path traversal attempts."""
        if cls.PATH_TRAVERSAL_PATTERN.search(str(value)):
            security_logger.warning(
                f"Potential path traversal detected: {value[:100]}"
            )
            return True
        return False
    
    @classmethod
    def validate_email(cls, email):
        """Validate email format."""
        return bool(cls.EMAIL_PATTERN.match(str(email)))
    
    @classmethod
    def validate_phone(cls, phone):
        """Validate phone number format."""
        return bool(cls.PHONE_PATTERN.match(str(phone)))
    
    @classmethod
    def validate_name(cls, name):
        """Validate name (letters, spaces, hyphens, apostrophes)."""
        if not name or len(name) < 2:
            return False
        return bool(re.match(r"^[a-zA-Z\s\-']{2,100}$", str(name)))
    
    @classmethod
    def is_safe_input(cls, value):
        """
        Check if input is safe from common attack vectors.
        
        Returns:
            Tuple of (is_safe, threat_type)
        """
        if cls.check_sql_injection(value):
            return False, 'SQL Injection'
        if cls.check_xss(value):
            return False, 'XSS'
        if cls.check_path_traversal(value):
            return False, 'Path Traversal'
        return True, None


def validate_input(*fields_to_check):
    """
    Decorator to validate form input against attack vectors.
    
    Args:
        fields_to_check: Field names to validate (checks all form fields if empty)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                # Get form data
                form_data = request.form.to_dict()
                
                # Determine which fields to check
                fields = fields_to_check if fields_to_check else form_data.keys()
                
                for field in fields:
                    value = form_data.get(field, '')
                    if value:
                        is_safe, threat_type = InputValidator.is_safe_input(value)
                        if not is_safe:
                            security_logger.warning(
                                f"{threat_type} attempt detected in field '{field}' "
                                f"from IP {request.remote_addr}"
                            )
                            abort(400)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class LoginAttemptTracker:
    """
    Track failed login attempts for brute force protection.
    """
    
    def __init__(self, max_attempts=5, lockout_duration=900):
        """
        Args:
            max_attempts: Maximum failed attempts before lockout
            lockout_duration: Lockout duration in seconds (default 15 minutes)
        """
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        self.failed_attempts = defaultdict(list)
        self.locked_accounts = {}
    
    def _get_key(self, identifier):
        """Create a hash key for the identifier."""
        return hashlib.sha256(str(identifier).encode()).hexdigest()[:16]
    
    def _cleanup_old_attempts(self, key):
        """Remove attempts older than lockout duration."""
        cutoff = datetime.utcnow() - timedelta(seconds=self.lockout_duration)
        self.failed_attempts[key] = [
            t for t in self.failed_attempts[key] if t > cutoff
        ]
    
    def is_locked(self, identifier):
        """Check if an account/IP is locked."""
        key = self._get_key(identifier)
        
        if key in self.locked_accounts:
            if datetime.utcnow() < self.locked_accounts[key]:
                remaining = (self.locked_accounts[key] - datetime.utcnow()).seconds
                return True, remaining
            else:
                del self.locked_accounts[key]
        
        return False, 0
    
    def record_failure(self, identifier):
        """
        Record a failed login attempt.
        
        Returns:
            Tuple of (is_locked, attempts_remaining)
        """
        key = self._get_key(identifier)
        
        # Clean up old attempts
        self._cleanup_old_attempts(key)
        
        # Record this attempt
        self.failed_attempts[key].append(datetime.utcnow())
        
        attempts = len(self.failed_attempts[key])
        
        if attempts >= self.max_attempts:
            # Lock the account
            self.locked_accounts[key] = (
                datetime.utcnow() + timedelta(seconds=self.lockout_duration)
            )
            security_logger.warning(
                f"Account locked due to {attempts} failed attempts: {identifier}"
            )
            return True, 0
        
        return False, self.max_attempts - attempts
    
    def record_success(self, identifier):
        """Clear failed attempts after successful login."""
        key = self._get_key(identifier)
        if key in self.failed_attempts:
            del self.failed_attempts[key]
        if key in self.locked_accounts:
            del self.locked_accounts[key]


# Global login tracker
login_tracker = LoginAttemptTracker()


def generate_secure_token(length=32):
    """Generate a cryptographically secure random token."""
    import secrets
    return secrets.token_urlsafe(length)


def hash_for_logging(sensitive_data):
    """Hash sensitive data for safe logging."""
    return hashlib.sha256(str(sensitive_data).encode()).hexdigest()[:8]


def log_security_event(event_type, details, level='warning'):
    """
    Log a security event.
    
    Args:
        event_type: Type of security event
        details: Event details
        level: Log level ('info', 'warning', 'error', 'critical')
    """
    message = f"[{event_type}] {details} - IP: {request.remote_addr if request else 'N/A'}"
    
    log_func = getattr(security_logger, level, security_logger.warning)
    log_func(message)


# Security middleware for Flask app
def init_security(app):
    """
    Initialize security features for the Flask app.
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def security_checks():
        """Perform security checks before each request."""
        # Check for blocked IPs
        ip = rate_limiter._get_client_ip()
        if rate_limiter.is_blocked(ip):
            abort(403)
        
        # Log suspicious user agents
        user_agent = request.headers.get('User-Agent', '')
        suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'masscan', 'zgrab']
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            log_security_event('SUSPICIOUS_AGENT', f"User-Agent: {user_agent}")
            rate_limiter.block_ip(ip, 3600)  # Block for 1 hour
            abort(403)
    
    @app.after_request
    def add_rate_limit_headers(response):
        """Add rate limit headers to response."""
        if hasattr(g, 'rate_limit_remaining'):
            response.headers['X-RateLimit-Remaining'] = g.rate_limit_remaining
        if hasattr(g, 'rate_limit_reset'):
            response.headers['X-RateLimit-Reset'] = g.rate_limit_reset
        return response
    
    return app
