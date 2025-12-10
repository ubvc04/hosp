@echo off
REM ============================================
REM Hospital Patient Portal - Windows Setup Script
REM ============================================
REM This script sets up the complete development environment
REM for the Hospital Patient Portal application.
REM ============================================

echo.
echo ============================================
echo   Hospital Patient Portal Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Create virtual environment
echo.
echo [INFO] Creating virtual environment...
if exist venv (
    echo [INFO] Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
)

REM Activate virtual environment and install dependencies
echo.
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [INFO] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies installed.

REM Create necessary directories
echo.
echo [INFO] Creating necessary directories...
if not exist "instance" mkdir instance
if not exist "keys" mkdir keys
if not exist "uploads" mkdir uploads
if not exist "uploads\reports" mkdir uploads\reports
echo [OK] Directories created.

REM Check for .env file
echo.
if not exist ".env" (
    echo [INFO] Creating .env file from template...
    (
        echo # Hospital Patient Portal Environment Configuration
        echo # ================================================
        echo.
        echo # Flask Configuration
        echo FLASK_ENV=development
        echo SECRET_KEY=your-super-secret-key-change-in-production-minimum-32-chars
        echo.
        echo # Database
        echo DATABASE_URL=sqlite:///instance/hospital.db
        echo.
        echo # Google Gemini API Key ^(for AI suggestions^)
        echo # Get your key from: https://aistudio.google.com/apikey
        echo GEMINI_API_KEY=your-gemini-api-key-here
        echo.
        echo # Security Settings
        echo SESSION_COOKIE_SECURE=False
        echo SESSION_COOKIE_HTTPONLY=True
        echo SESSION_COOKIE_SAMESITE=Lax
    ) > .env
    echo [OK] .env file created. Please update it with your settings.
) else (
    echo [OK] .env file already exists.
)

REM Initialize database
echo.
echo [INFO] Initializing database with sample data...
python init_db.py
if errorlevel 1 (
    echo [ERROR] Failed to initialize database.
    pause
    exit /b 1
)
echo [OK] Database initialized.

REM Display success message
echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo To start the application:
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate
echo   2. Run the application:
echo      python app.py
echo.
echo Login Credentials:
echo   Admin:   baveshchowdary1@gmail.com / bavesh1234
echo   Patient: john.doe@email.com / Patient@123
echo.
echo Application URL: http://127.0.0.1:5000
echo ============================================
echo.
pause
