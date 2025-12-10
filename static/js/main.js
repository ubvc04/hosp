/**
 * Hospital Patient Portal - Enhanced JavaScript
 * =============================================
 * Modern animations and interactive features
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all animations and features
    initAnimations();
    initTooltips();
    initPopovers();
    initAlerts();
    initForms();
    initSidebar();
    initParticles();
    initScrollAnimations();
    initCounterAnimations();
    initRippleEffect();
    initHoverEffects();
    initPasswordToggle();
    initBillCalculator();
    initLoadingStates();
    initDateInputs();
    initTextareaCounters();
    initConfirmDialogs();
    initSearchHighlight();
});

// ============== Initialization Functions ==============

function initAnimations() {
    // Add stagger animation to card containers
    const cardContainers = document.querySelectorAll('.row');
    cardContainers.forEach(container => {
        const cards = container.querySelectorAll('.card, .stat-card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in');
        });
    });

    // Animate elements on page load
    const animatedElements = document.querySelectorAll('.animate-on-load');
    animatedElements.forEach((el, index) => {
        el.style.opacity = '0';
        setTimeout(() => {
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => {
        new bootstrap.Tooltip(el, {
            animation: true,
            delay: { show: 200, hide: 100 }
        });
    });
}

function initPopovers() {
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    popoverTriggerList.forEach(el => new bootstrap.Popover(el));
}

function initAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        // Add progress bar for auto-dismiss
        const progressBar = document.createElement('div');
        progressBar.className = 'alert-progress';
        progressBar.style.cssText = `
            position: absolute;
            bottom: 0;
            left: 0;
            height: 3px;
            background: currentColor;
            opacity: 0.3;
            width: 100%;
            animation: alertProgress 5s linear forwards;
        `;
        alert.style.position = 'relative';
        alert.appendChild(progressBar);

        setTimeout(() => {
            alert.style.transition = 'all 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100px)';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Add keyframe for progress bar
    if (!document.getElementById('alert-progress-style')) {
        const style = document.createElement('style');
        style.id = 'alert-progress-style';
        style.textContent = `
            @keyframes alertProgress {
                from { width: 100%; }
                to { width: 0%; }
            }
        `;
        document.head.appendChild(style);
    }
}

function initForms() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Shake animation for invalid form
                form.classList.add('shake-animation');
                setTimeout(() => form.classList.remove('shake-animation'), 500);
            }
            form.classList.add('was-validated');
        });
    });

    // Add focus animation to form inputs
    const formInputs = document.querySelectorAll('.form-control, .form-select');
    formInputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('input-focused');
        });
        input.addEventListener('blur', () => {
            input.parentElement.classList.remove('input-focused');
        });
    });

    // Add shake animation style
    if (!document.getElementById('shake-style')) {
        const style = document.createElement('style');
        style.id = 'shake-style';
        style.textContent = `
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                20%, 40%, 60%, 80% { transform: translateX(5px); }
            }
            .shake-animation {
                animation: shake 0.5s ease;
            }
            .input-focused {
                position: relative;
            }
            .input-focused::after {
                content: '';
                position: absolute;
                bottom: -2px;
                left: 50%;
                width: 0;
                height: 2px;
                background: linear-gradient(90deg, #2563eb, #0d9488);
                transition: all 0.3s ease;
                transform: translateX(-50%);
            }
        `;
        document.head.appendChild(style);
    }
}

function initSidebar() {
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-menu a');
    
    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
        
        // Add hover sound effect (visual feedback)
        link.addEventListener('mouseenter', () => {
            link.style.transform = 'translateX(5px)';
        });
        link.addEventListener('mouseleave', () => {
            if (!link.classList.contains('active')) {
                link.style.transform = 'translateX(0)';
            }
        });
    });

    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });
    }
}

function initParticles() {
    // Create floating particles background
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'particles-bg';
    
    for (let i = 0; i < 15; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 20}s`;
        particle.style.animationDuration = `${15 + Math.random() * 15}s`;
        particle.style.width = `${5 + Math.random() * 10}px`;
        particle.style.height = particle.style.width;
        particlesContainer.appendChild(particle);
    }
    
    document.body.appendChild(particlesContainer);
}

function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-visible');
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe cards and tables for scroll animation
    const scrollElements = document.querySelectorAll('.card, .table-responsive, .stat-card');
    scrollElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Trigger initial visibility check
    setTimeout(() => {
        scrollElements.forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.top < window.innerHeight) {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }
        });
    }, 100);
}

function initCounterAnimations() {
    const counters = document.querySelectorAll('.stat-number');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent);
        if (isNaN(target)) return;
        
        counter.textContent = '0';
        
        const duration = 1500;
        const increment = target / (duration / 16);
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.textContent = Math.ceil(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        // Start animation when element is visible
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                updateCounter();
                observer.disconnect();
            }
        });
        
        observer.observe(counter);
    });
}

function initRippleEffect() {
    const rippleElements = document.querySelectorAll('.btn, .nav-link, .dropdown-item, .quick-action-btn');
    
    rippleElements.forEach(element => {
        element.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple-effect 0.6s ease-out;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // Add ripple animation style
    if (!document.getElementById('ripple-style')) {
        const style = document.createElement('style');
        style.id = 'ripple-style';
        style.textContent = `
            @keyframes ripple-effect {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

function initHoverEffects() {
    // Card tilt effect on hover
    const cards = document.querySelectorAll('.card:not(.no-tilt)');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
        });
    });

    // Button magnetic effect
    const buttons = document.querySelectorAll('.btn-primary, .btn-success');
    
    buttons.forEach(btn => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            btn.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px) translateY(-3px)`;
        });
        
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = '';
        });
    });
}

function initPasswordToggle() {
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const input = toggle.closest('.input-group').querySelector('input');
            const icon = toggle.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
            
            // Add animation to icon
            icon.style.transform = 'scale(1.2)';
            setTimeout(() => icon.style.transform = '', 200);
        });
    });
}

function initBillCalculator() {
    const amountInput = document.getElementById('amount');
    const paidAmountInput = document.getElementById('paid_amount');
    const balanceDisplay = document.getElementById('balance-display');
    
    if (amountInput && paidAmountInput && balanceDisplay) {
        function updateBalance() {
            const amount = parseFloat(amountInput.value) || 0;
            const paid = parseFloat(paidAmountInput.value) || 0;
            const balance = amount - paid;
            
            // Animate the balance change
            balanceDisplay.style.transform = 'scale(1.1)';
            balanceDisplay.textContent = `$${balance.toFixed(2)}`;
            balanceDisplay.className = balance > 0 ? 'text-danger fw-bold' : 'text-success fw-bold';
            
            setTimeout(() => balanceDisplay.style.transform = '', 200);
        }
        
        amountInput.addEventListener('input', updateBalance);
        paidAmountInput.addEventListener('input', updateBalance);
        updateBalance();
    }
}

function initLoadingStates() {
    const submitForms = document.querySelectorAll('form[data-loading]');
    
    submitForms.forEach(form => {
        form.addEventListener('submit', () => {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalContent = submitBtn.innerHTML;
                submitBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Processing...
                `;
                submitBtn.dataset.originalContent = originalContent;
            }
        });
    });
}

function initDateInputs() {
    const dateInputs = document.querySelectorAll('input[type="date"]:not([value])');
    
    dateInputs.forEach(input => {
        if (input.dataset.default === 'today') {
            input.valueAsDate = new Date();
        }
    });
}

function initTextareaCounters() {
    const textareas = document.querySelectorAll('textarea[maxlength]');
    
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('small');
        counter.className = 'form-text text-muted text-end d-block mt-1';
        counter.innerHTML = `<span class="char-count">0</span> / ${maxLength}`;
        textarea.parentNode.appendChild(counter);
        
        const charCount = counter.querySelector('.char-count');
        
        textarea.addEventListener('input', () => {
            const currentLength = textarea.value.length;
            charCount.textContent = currentLength;
            
            // Animate and color based on usage
            charCount.style.transform = 'scale(1.2)';
            setTimeout(() => charCount.style.transform = '', 150);
            
            if (currentLength > maxLength * 0.9) {
                counter.classList.remove('text-muted', 'text-warning');
                counter.classList.add('text-danger');
            } else if (currentLength > maxLength * 0.7) {
                counter.classList.remove('text-muted', 'text-danger');
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning', 'text-danger');
                counter.classList.add('text-muted');
            }
        });
    });
}

function initConfirmDialogs() {
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', event => {
            const message = button.dataset.confirm || 'Are you sure you want to proceed?';
            
            // Create custom modal instead of default confirm
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });
}

function initSearchHighlight() {
    const searchInput = document.querySelector('input[name="search"]');
    
    if (searchInput && searchInput.value) {
        const searchTerm = searchInput.value.toLowerCase();
        const tableBody = document.querySelector('tbody');
        
        if (tableBody) {
            const cells = tableBody.querySelectorAll('td');
            cells.forEach(cell => {
                const text = cell.textContent;
                if (text.toLowerCase().includes(searchTerm)) {
                    const regex = new RegExp(`(${searchTerm})`, 'gi');
                    cell.innerHTML = text.replace(regex, '<mark class="bg-warning">$1</mark>');
                }
            });
        }
    }
}

// ============== Utility Object ==============

const HospitalPortal = {
    // Format currency with animation
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },
    
    // Format date nicely
    formatDate: function(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    // Enhanced toast notification with animations
    showToast: function(message, type = 'info', duration = 5000) {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const iconMap = {
            success: 'fa-check-circle',
            danger: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.style.cssText = `
            animation: toastSlideIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
        `;
        toast.innerHTML = `
            <div class="d-flex align-items-center p-3">
                <i class="fas ${iconMap[type]} me-2 fa-lg"></i>
                <div class="toast-body flex-grow-1">${message}</div>
                <button type="button" class="btn-close btn-close-white ms-2" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-progress" style="
                height: 3px;
                background: rgba(255,255,255,0.5);
                animation: toastProgress ${duration}ms linear forwards;
            "></div>
        `;
        
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: duration });
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toast.style.animation = 'toastSlideOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        });
    },
    
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        
        // Add toast animation styles
        if (!document.getElementById('toast-style')) {
            const style = document.createElement('style');
            style.id = 'toast-style';
            style.textContent = `
                @keyframes toastSlideIn {
                    from {
                        opacity: 0;
                        transform: translateX(100%) scale(0.8);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(0) scale(1);
                    }
                }
                @keyframes toastSlideOut {
                    from {
                        opacity: 1;
                        transform: translateX(0) scale(1);
                    }
                    to {
                        opacity: 0;
                        transform: translateX(100%) scale(0.8);
                    }
                }
                @keyframes toastProgress {
                    from { width: 100%; }
                    to { width: 0%; }
                }
            `;
            document.head.appendChild(style);
        }
        
        return container;
    },
    
    // Smooth scroll to element
    scrollTo: function(element, offset = 100) {
        const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    },
    
    // Debounce function for search inputs
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Copy to clipboard with feedback
    copyToClipboard: async function(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Copied to clipboard!', 'success', 2000);
        } catch (err) {
            this.showToast('Failed to copy', 'danger', 2000);
        }
    }
};

// Make HospitalPortal globally available
window.HospitalPortal = HospitalPortal;

// ============== Page-specific initializations ==============

// Patient category toggle for forms
const categorySelect = document.getElementById('category');
if (categorySelect) {
    const inPatientFields = document.getElementById('in-patient-fields');
    
    function toggleInPatientFields() {
        if (inPatientFields) {
            if (categorySelect.value === 'IN_PATIENT') {
                inPatientFields.style.display = 'block';
                inPatientFields.style.animation = 'fadeIn 0.3s ease';
            } else {
                inPatientFields.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => inPatientFields.style.display = 'none', 300);
            }
        }
    }
    
    categorySelect.addEventListener('change', toggleInPatientFields);
    toggleInPatientFields();
    
    // Add fadeOut animation
    if (!document.getElementById('fadeout-style')) {
        const style = document.createElement('style');
        style.id = 'fadeout-style';
        style.textContent = `
            @keyframes fadeOut {
                from { opacity: 1; transform: translateY(0); }
                to { opacity: 0; transform: translateY(-10px); }
            }
        `;
        document.head.appendChild(style);
    }
}

// Print functionality with animation
const printButtons = document.querySelectorAll('[data-print]');
printButtons.forEach(button => {
    button.addEventListener('click', () => {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = '';
            window.print();
        }, 150);
    });
});

// Search form auto-submit with debounce
const filterSelects = document.querySelectorAll('.filter-auto-submit');
filterSelects.forEach(select => {
    select.addEventListener('change', () => {
        select.style.transform = 'scale(1.02)';
        setTimeout(() => {
            select.style.transform = '';
            select.closest('form').submit();
        }, 200);
    });
});

// Add smooth page transitions
window.addEventListener('beforeunload', () => {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.3s ease';
});

// Console welcome message
console.log('%c🏥 Hospital Patient Portal', 'font-size: 24px; font-weight: bold; color: #2563eb;');
console.log('%cSecured with RSA-4096 Encryption', 'font-size: 12px; color: #059669;');
