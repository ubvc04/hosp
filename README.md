# 🏥 Hospital Patient Portal

A complete, advanced Hospital Patient Portal web application with a strong focus on **security**, **asymmetric encryption (RSA-4096)**, and a **polished healthcare UI**.

![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)
![Security](https://img.shields.io/badge/Encryption-RSA--4096-red)

## ✨ Features

### 🔐 Security
- **RSA-4096 Asymmetric Encryption** for all sensitive patient data
- **Hybrid Encryption** (AES + RSA) for large data fields
- **bcrypt Password Hashing** with secure salt rounds
- **CSRF Protection** on all forms
- **Role-Based Access Control** (Admin/Patient)
- **Secure Session Management** with Flask-Login

### 👨‍💼 Admin Features
- Complete **CRUD operations** for patient management
- Manage patient **visits**, **bills**, and **medical reports**
- View all encrypted data with automatic decryption
- Dashboard with statistics and recent activity
- Search and filter patients

### 👤 Patient Features
- **Read-only access** to personal medical records
- View visit history, bills, and reports
- **AI-powered health suggestions** based on medical history
- Secure profile management
- Password change functionality

### 🤖 AI Health Suggestions
- Integration with **Google Gemini API** for intelligent health recommendations
- **Rule-based fallback system** for reliable suggestions
- Personalized advice based on:
  - Medical history
  - Recent diagnoses
  - Current prescriptions
  - Age-appropriate recommendations

### 🎨 Modern UI
- **Bootstrap 5** responsive design
- Healthcare-themed color scheme
- Clean, intuitive navigation
- Mobile-friendly interface
- Professional data tables and cards

## 📁 Project Structure

```
Hosp/
├── app.py                    # Main Flask application
├── models.py                 # SQLAlchemy database models
├── auth.py                   # Authentication routes & decorators
├── admin_routes.py           # Admin CRUD routes
├── patient_routes.py         # Patient view routes
├── crypto_utils.py           # RSA-4096 encryption utilities
├── ai_suggestions.py         # AI health suggestion engine
├── forms.py                  # WTForms form definitions
├── config.py                 # Application configuration
├── init_db.py                # Database initialization script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .gitignore                # Git ignore rules
├── keys/                     # RSA key storage (auto-generated)
│   ├── private_key.pem
│   └── public_key.pem
├── static/
│   ├── css/
│   │   └── style.css         # Custom styles
│   └── js/
│       └── main.js           # Frontend JavaScript
└── templates/
    ├── base.html             # Base template
    ├── auth/
    │   ├── login.html
    │   ├── profile.html
    │   └── change_password.html
    ├── admin/
    │   ├── admin_navbar.html
    │   ├── dashboard.html
    │   ├── patients.html
    │   ├── add_patient.html
    │   ├── edit_patient.html
    │   ├── view_patient.html
    │   ├── visits.html
    │   ├── add_visit.html
    │   ├── edit_visit.html
    │   ├── bills.html
    │   ├── add_bill.html
    │   ├── edit_bill.html
    │   ├── reports.html
    │   ├── add_report.html
    │   └── edit_report.html
    ├── patient/
    │   ├── patient_navbar.html
    │   ├── dashboard.html
    │   ├── records.html
    │   ├── bills.html
    │   └── reports.html
    └── errors/
        ├── 403.html
        ├── 404.html
        └── 500.html
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download** the project to your local machine

2. **Navigate to the project directory**:
   ```bash
   cd Hosp
   ```

3. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize the database**:
   ```bash
   python init_db.py
   ```

6. **Run the application**:
   ```bash
   python app.py
   ```

7. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## 🔑 Default Login Credentials

### Administrator Account
- **Email**: `baveshchowdary1@gmail.com`
- **Password**: `bavesh1234`

### Sample Patient Accounts
- **Email**: `john.doe@email.com` / **Password**: `Patient@123`
- **Email**: `sarah.smith@email.com` / **Password**: `Patient@123`
- **Email**: `robert.johnson@email.com` / **Password**: `Patient@123`

> ⚠️ **Important**: Change these default credentials in a production environment!

## 🔒 Security Architecture

### Encryption Flow
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Plain Text    │────▶│  RSA-4096 Public │────▶│  Encrypted Data │
│   (Patient Data)│     │    Key Encrypt   │     │   (Stored in DB)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Plain Text    │◀────│  RSA-4096 Private│◀────│  Encrypted Data │
│   (Displayed)   │     │    Key Decrypt   │     │   (From DB)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Encrypted Fields
The following sensitive data fields are encrypted at rest:
- `encrypted_address` - Patient home address
- `encrypted_medical_history` - Complete medical history
- `encrypted_diagnosis` - Visit diagnoses
- `encrypted_prescriptions` - Medication prescriptions
- `encrypted_bill_details` - Billing itemization
- `encrypted_report_summary` - Medical report summaries

### Password Security
- Passwords are hashed using **bcrypt** with 12 salt rounds
- Original passwords are never stored
- Secure comparison prevents timing attacks

## 🤖 AI Suggestions Configuration

The AI suggestion engine uses Google's Gemini API with a fallback rule-based system.

### How It Works
1. Patient's decrypted medical data is analyzed
2. Gemini API generates personalized health suggestions
3. If API fails, rule-based engine provides recommendations
4. Suggestions cover diet, exercise, medication, and lifestyle

### Customizing AI Behavior
Edit `ai_suggestions.py` to modify:
- API parameters (temperature, max tokens)
- Rule-based conditions and recommendations
- Suggestion categories and priorities

## 📊 Database Schema

### User Table
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| username | String(80) | Unique username |
| email | String(120) | User email |
| password_hash | String(255) | bcrypt hashed password |
| role | Enum | ADMIN or PATIENT |
| patient_id | String(20) | Links to Patient (nullable) |

### Patient Table
| Field | Type | Description |
|-------|------|-------------|
| patient_id | String(20) | Primary key (e.g., "P001") |
| first_name | String(50) | Patient first name |
| last_name | String(50) | Patient last name |
| date_of_birth | Date | Birth date |
| gender | String(10) | Gender |
| phone | String(20) | Contact phone |
| email | String(120) | Contact email |
| blood_group | String(5) | Blood type |
| encrypted_address | Text | RSA encrypted address |
| encrypted_medical_history | Text | RSA encrypted history |
| emergency_contact_name | String(100) | Emergency contact |
| emergency_contact_phone | String(20) | Emergency phone |

### Visit Table
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| patient_id | String(20) | Foreign key to Patient |
| visit_date | DateTime | Visit timestamp |
| visit_type | String(50) | Type of visit |
| doctor_name | String(100) | Attending physician |
| department | String(50) | Hospital department |
| encrypted_diagnosis | Text | RSA encrypted diagnosis |
| encrypted_prescriptions | Text | RSA encrypted prescriptions |
| notes | Text | Additional notes |

### Bill Table
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| patient_id | String(20) | Foreign key to Patient |
| bill_date | DateTime | Bill generation date |
| total_amount | Float | Total bill amount |
| paid_amount | Float | Amount paid |
| payment_status | String(20) | PENDING/PARTIAL/PAID |
| encrypted_bill_details | Text | RSA encrypted itemization |

### Report Table
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| patient_id | String(20) | Foreign key to Patient |
| report_type | String(100) | Type of report |
| report_date | DateTime | Report date |
| encrypted_report_summary | Text | RSA encrypted summary |
| file_path | String(255) | Path to report file |
| created_by | String(100) | Report creator |

## 🛠️ Development

### Running in Debug Mode
```bash
# Set environment variable
set FLASK_DEBUG=1  # Windows
export FLASK_DEBUG=1  # Linux/macOS

python app.py
```

### Resetting the Database
```bash
# Delete existing database
del hospital.db  # Windows
rm hospital.db   # Linux/macOS

# Reinitialize
python init_db.py
```

### Regenerating Encryption Keys
```bash
# Delete existing keys
rmdir /s /q keys  # Windows
rm -rf keys       # Linux/macOS

# Keys auto-generate on next app start
python app.py
```

> ⚠️ **Warning**: Regenerating keys will make existing encrypted data unreadable!

## 🌐 Environment Variables

Configure these in `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| SECRET_KEY | auto-generated | Flask session secret |
| DATABASE_URL | sqlite:///hospital.db | Database connection string |
| GEMINI_API_KEY | (configured) | Google Gemini API key |
| FLASK_DEBUG | False | Enable debug mode |

## 📝 API Reference

### Authentication Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/login` | GET, POST | User login |
| `/logout` | GET | User logout |
| `/profile` | GET | View user profile |
| `/change-password` | GET, POST | Change password |

### Admin Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/admin/dashboard` | GET | Admin dashboard |
| `/admin/patients` | GET | List all patients |
| `/admin/patients/add` | GET, POST | Add new patient |
| `/admin/patients/<id>` | GET | View patient details |
| `/admin/patients/<id>/edit` | GET, POST | Edit patient |
| `/admin/patients/<id>/delete` | POST | Delete patient |
| `/admin/visits` | GET | List all visits |
| `/admin/bills` | GET | List all bills |
| `/admin/reports` | GET | List all reports |

### Patient Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/patient/dashboard` | GET | Patient dashboard with AI suggestions |
| `/patient/records` | GET | View medical records |
| `/patient/bills` | GET | View bills |
| `/patient/reports` | GET | View reports |

## 🧪 Testing

### Manual Testing Checklist
- [ ] Admin login works
- [ ] Patient login works
- [ ] Admin can CRUD patients
- [ ] Admin can manage visits, bills, reports
- [ ] Patient can only view own data
- [ ] Encrypted data displays correctly when decrypted
- [ ] AI suggestions appear on patient dashboard
- [ ] Password change works
- [ ] Unauthorized access is blocked

## 🔧 Troubleshooting

### Common Issues

**"Encryption key not found"**
- Ensure `keys/` directory exists
- Run `python app.py` to auto-generate keys

**"Database locked"**
- Close other applications using the database
- Restart the Flask server

**"Module not found"**
- Activate virtual environment
- Run `pip install -r requirements.txt`

**"AI suggestions not working"**
- Check Gemini API key in `.env`
- Rule-based fallback will activate automatically

## 📄 License

This project is for educational purposes. Use responsibly and ensure compliance with healthcare data regulations (HIPAA, GDPR, etc.) in production environments.

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📞 Support

For issues and questions, please open an issue on the project repository.

---

**Built with ❤️ for Healthcare**
