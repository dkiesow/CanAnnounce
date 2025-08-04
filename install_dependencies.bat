@echo off
REM Installation script for Can Announce on Windows
echo Can Announce Installation Script
echo ====================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is required but not installed.
    echo Please install Python 3.7+ and run this script again.
    pause
    exit /b 1
)

echo Python found:
python --version

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo Installation failed. Trying alternative methods...
    pip install Flask==2.3.3 requests==2.31.0 Werkzeug==2.3.7
    pip install PyQt5==5.15.9 PyQtWebEngine==5.15.6
)

echo.
echo Installation complete!
echo.
echo Next Steps:
echo 1. Copy config_template.py to config.py
echo 2. Edit config.py with your Canvas and TinyMCE credentials
echo 3. Run: python main.py
echo.
pause
