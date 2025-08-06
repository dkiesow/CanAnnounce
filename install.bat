@echo off
REM Quick install script for CanAnnounce (Windows)

echo 🎯 CanAnnounce Quick Install
echo ============================

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install the package in development mode
echo 📥 Installing CanAnnounce...
pip install -e .

echo.
echo ✅ Installation complete!
echo.
echo 🚀 Next steps:
echo 1. Run configuration setup: canannounce-setup
echo 2. Start the application: canannounce
echo.
echo 📁 To activate this environment later:
echo    venv\Scripts\activate.bat

pause
