#!/bin/bash
# ============================================
# Hospital Patient Portal - Linux/Mac Setup Script
# ============================================
# This script sets up the complete development environment
# for the Hospital Patient Portal application.
# ============================================

set -e

echo ""
echo "============================================"
echo "  Hospital Patient Portal Setup"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "Please install Python 3.9+ using your package manager."
    exit 1
fi

echo "[OK] Python found"
python3 --version

# Create virtual environment
echo ""
echo "[INFO] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "[INFO] Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "[OK] Virtual environment created."
fi

# Activate virtual environment
echo ""
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

echo "[INFO] Upgrading pip..."
pip install --upgrade pip

echo ""
echo "[INFO] Installing dependencies..."
pip install -r requirements.txt
echo "[OK] Dependencies installed."

# Create necessary directories
echo ""
echo "[INFO] Creating necessary directories..."
mkdir -p instance
mkdir -p keys
mkdir -p uploads/reports
echo "[OK] Directories created."

# Check for .env file
echo ""
if [ ! -f ".env" ]; then
    echo "[INFO] Creating .env file from template..."
    cat > .env << 'EOF'
# Hospital Patient Portal Environment Configuration
# ================================================

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-in-production-minimum-32-chars

# Database
DATABASE_URL=sqlite:///instance/hospital.db

# Google Gemini API Key (for AI suggestions)
# Get your key from: https://aistudio.google.com/apikey
GEMINI_API_KEY=your-gemini-api-key-here

# Security Settings
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
EOF
    echo "[OK] .env file created. Please update it with your settings."
else
    echo "[OK] .env file already exists."
fi

# Initialize database
echo ""
echo "[INFO] Initializing database with sample data..."
python init_db.py
echo "[OK] Database initialized."

# Display success message
echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "To start the application:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo "  2. Run the application:"
echo "     python app.py"
echo ""
echo "Login Credentials:"
echo "  Admin:   baveshchowdary1@gmail.com / bavesh1234"
echo "  Patient: john.doe@email.com / Patient@123"
echo ""
echo "Application URL: http://127.0.0.1:5000"
echo "============================================"
echo ""
