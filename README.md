# 🏥 Hospital Patient Portal - Blockchain Edition

A secure hospital patient management system with **RSA-4096 encryption** and **Blockchain integration** using Ganache.

![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Blockchain](https://img.shields.io/badge/Blockchain-Ganache-orange)
![Security](https://img.shields.io/badge/Encryption-RSA--4096-red)

## 🔐 Security Features

### Encryption Layer
- **RSA-4096** encryption for sensitive medical data
- Encrypted fields: medical history, diagnosis, prescriptions, billing details
- Hybrid encryption (AES + RSA) for large data

### Blockchain Layer
- **Ganache** local Ethereum blockchain
- **Smart Contract** for immutable record storage
- **Tamper-proof** audit trail
- **Data integrity verification**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Flask Templates)                │
├─────────────────────────────────────────────────────────────┤
│                    Flask Application                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Auth Routes │  │Admin Routes │  │ Blockchain Routes   │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌─────────────────────────────┐  │
│  │    SQLite + RSA     │  │   Ganache Blockchain        │  │
│  │  (Encrypted Data)   │  │   (Hash Verification)       │  │
│  └─────────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

### 👨‍💼 Admin Features
- Complete **CRUD operations** for patient management
- Manage patient **visits**, **bills**, and **medical reports**
- **Blockchain Dashboard** for monitoring
- View audit logs and data integrity
- Search and filter patients

### 👤 Patient Features
- **Read-only access** to personal medical records
- View visit history, bills, and reports
- **AI-powered health suggestions**
- Secure profile management

### ⛓️ Blockchain Features
- Automatic syncing of records to blockchain
- Verify data integrity at any time
- Immutable audit trail
- Tamper detection

## 📋 Prerequisites

1. **Python 3.10+**
2. **Node.js** (optional, for Ganache GUI)
3. **Ganache** - Download from https://trufflesuite.com/ganache/

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/ubvc04/hosp.git
cd hosp
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create `.env` file:
```env
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=development

# Email Configuration (Gmail)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Blockchain (added after deployment)
GANACHE_URL=http://127.0.0.1:7545
```

### 5. Initialize Database
```bash
python init_db.py
```

### 6. Run Application
```bash
python app.py
```

Access at: http://localhost:5000

---

## ⛓️ Blockchain Setup

### Step 1: Start Ganache

1. Open **Ganache** application
2. Click **"QUICKSTART ETHEREUM"** or create workspace
3. Note the RPC Server URL (default: `http://127.0.0.1:7545`)

### Step 2: Deploy Smart Contract

```bash
python deploy_contract.py
```

This will:
- Install Solidity compiler
- Compile `contracts/PatientRecords.sol`
- Deploy to Ganache
- Save contract address to `.env`

### Step 3: Configure Private Key

1. In Ganache, click the **key icon** 🔑 next to first account
2. Copy the private key
3. Add to `.env`:
```env
BLOCKCHAIN_PRIVATE_KEY=0x...your-private-key...
CONTRACT_ADDRESS=0x...deployed-address...
```

### Step 4: Access Blockchain Dashboard

1. Login as admin
2. Navigate to **Blockchain** in navbar
3. View status, sync patients, check audit logs

---

## 📁 Project Structure

```
hosp/
├── contracts/
│   └── PatientRecords.sol      # Solidity smart contract
├── templates/
│   ├── admin/
│   │   ├── blockchain_dashboard.html
│   │   └── ...
│   ├── auth/
│   └── patient/
├── app.py                      # Flask application factory
├── blockchain.py               # Blockchain manager class
├── blockchain_routes.py        # Blockchain API endpoints
├── deploy_contract.py          # Contract deployment script
├── models.py                   # SQLAlchemy models
├── crypto_utils.py             # RSA encryption utilities
├── admin_routes.py             # Admin functionality
├── patient_routes.py           # Patient functionality
├── auth.py                     # Authentication
├── config.py                   # Configuration
└── requirements.txt
```

---

## 🔗 How Blockchain Security Works

### Data Flow

1. **Patient data** entered via web interface
2. **Sensitive fields** encrypted with RSA-4096
3. **Encrypted data** stored in SQLite
4. **SHA-256 hash** of record generated
5. **Hash stored** on Ganache blockchain
6. **Audit log** created on blockchain

### Verification

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Database     │────►│ Generate     │────►│ Compare with │
│ Record       │     │ Hash         │     │ Blockchain   │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │ ✓ Valid OR   │
                                          │ ✗ Tampered   │
                                          └──────────────┘
```

### Benefits

| Feature | Benefit |
|---------|---------|
| **Immutability** | Records cannot be altered without detection |
| **Audit Trail** | Every access logged permanently |
| **Data Integrity** | Verify records haven't been tampered |
| **Transparency** | All transactions visible |
| **Non-repudiation** | Cannot deny actions taken |

---

## 🛡️ Smart Contract Functions

| Function | Description |
|----------|-------------|
| `addRecord()` | Store record hash on blockchain |
| `verifyRecord()` | Verify data integrity |
| `getPatientRecords()` | Get all records for patient |
| `getAuditLogs()` | Retrieve audit trail |
| `authorizeProvider()` | Add authorized provider |
| `revokeProvider()` | Remove authorization |

---

## 📡 API Endpoints

### Blockchain Status
```
GET /blockchain/status
```

### Store Record
```
POST /blockchain/store-record
{
  "patient_id": 1,
  "record_type": "VISIT",
  "data": { ... }
}
```

### Verify Record
```
POST /blockchain/verify-record
{
  "patient_id": 1,
  "record_index": 0,
  "data": { ... }
}
```

### Sync Patient
```
POST /blockchain/sync-patient/<patient_id>
```

---

## 🔧 Troubleshooting

### Ganache Connection Failed
**Solution:** Ensure Ganache is running on `http://127.0.0.1:7545`

### Contract Not Deployed
**Solution:** Run `python deploy_contract.py`

### Solidity Compiler Error
**Solution:** 
```bash
pip install py-solc-x
python -c "from solcx import install_solc; install_solc('0.8.19')"
```

---

## 🔐 Default Credentials

**Admin Account:**
- Email: `baveshchowdary1@gmail.com`
- Password: `amulya1234`

---

## 📄 License

MIT License

---

## 👨‍💻 Author

**Bavesh Chowdary**  
GitHub: [@ubvc04](https://github.com/ubvc04)
