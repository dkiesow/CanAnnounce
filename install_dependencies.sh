#!/bin/bash
"""
Installation script for Can Announce with PyQt5 fallback options
This script tries multiple methods to install PyQt5 on macOS
"""

echo "Can Announce Installation Script"
echo "===================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to test PyQt5 installation
test_pyqt5() {
    python3 -c "import PyQt5.QtWidgets; print('PyQt5 installation successful!')" 2>/dev/null
}

echo "Step 1: Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo ""
echo "Step 2: Attempting PyQt5 installation methods..."

# Method 1: Try with pre-compiled wheels only
echo "Method 1: Installing with pre-compiled wheels..."
pip install --only-binary=all PyQt5==5.15.9 PyQtWebEngine==5.15.6
if test_pyqt5; then
    echo "✅ PyQt5 installed successfully with pre-compiled wheels!"
    pip install Flask==2.3.3 requests==2.31.0 Werkzeug==2.3.7
    echo "✅ All dependencies installed!"
    exit 0
fi

# Method 2: Try with Homebrew Qt
if command_exists brew; then
    echo "Method 2: Installing Qt via Homebrew and then PyQt5..."
    brew install qt@5
    export PATH="/opt/homebrew/opt/qt@5/bin:$PATH"
    export LDFLAGS="-L/opt/homebrew/opt/qt@5/lib"
    export CPPFLAGS="-I/opt/homebrew/opt/qt@5/include"

    pip install PyQt5==5.15.9 PyQtWebEngine==5.15.6
    if test_pyqt5; then
        echo "✅ PyQt5 installed successfully with Homebrew Qt!"
        pip install Flask==2.3.3 requests==2.31.0 Werkzeug==2.3.7
        echo "✅ All dependencies installed!"
        exit 0
    fi
else
    echo "Homebrew not found, skipping Method 2..."
fi

# Method 3: Try with conda if available
if command_exists conda; then
    echo "Method 3: Installing PyQt5 via conda..."
    conda install -y pyqt=5.15.9
    if test_pyqt5; then
        echo "✅ PyQt5 installed successfully with conda!"
        pip install Flask==2.3.3 requests==2.31.0 Werkzeug==2.3.7
        echo "✅ All dependencies installed!"
        exit 0
    fi
else
    echo "Conda not found, skipping Method 3..."
fi

# Method 4: Try newer version
echo "Method 4: Trying with newer PyQt5 version..."
pip install PyQt5==5.15.10 PyQtWebEngine==5.15.6
if test_pyqt5; then
    echo "✅ PyQt5 installed successfully with newer version!"
    pip install Flask==2.3.3 requests==2.31.0 Werkzeug==2.3.7
    echo "✅ All dependencies installed!"
    exit 0
fi

echo ""
echo "❌ All PyQt5 installation methods failed."
echo ""
echo "Alternative options:"
echo "1. Use the web-only version: python main_web.py"
echo "2. Install PyQt5 manually through your system package manager"
echo "3. Use a Python virtual environment with a different Python version"
echo ""
echo "For manual installation, try:"
echo "  brew install pyqt@5"
echo "  pip install PyQt5"
