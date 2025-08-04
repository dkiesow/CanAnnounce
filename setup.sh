#!/bin/bash
"""
Canvas Announcer Setup Script
This script handles the complete setup process for new users
"""

echo "🎯 Canvas Announcer Setup"
echo "========================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.7+ and run this script again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is required but not installed."
    echo "Please install pip and run this script again."
    exit 1
fi

# Use pip3 if available, otherwise pip
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo "✅ pip found: $PIP_CMD"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
$PIP_CMD install --upgrade pip setuptools wheel

# Install dependencies using the automated installer
echo "🔧 Installing dependencies..."
if [ -f "install_dependencies.sh" ]; then
    chmod +x install_dependencies.sh
    ./install_dependencies.sh
else
    echo "⚠️  install_dependencies.sh not found, trying direct installation..."
    $PIP_CMD install -r requirements.txt
fi

# Setup configuration
echo ""
echo "⚙️  Setting up configuration..."
if [ ! -f "config.py" ]; then
    if [ -f "config_template.py" ]; then
        cp config_template.py config.py
        echo "✅ Created config.py from template"
    else
        echo "❌ config_template.py not found!"
        exit 1
    fi
else
    echo "ℹ️  config.py already exists, skipping copy"
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Next Steps:"
echo "1. Edit config.py with your Canvas and TinyMCE credentials"
echo "2. Get Canvas API token: Canvas → Account → Settings → New Access Token"
echo "3. Get TinyMCE API key: https://www.tiny.cloud/ (free account)"
echo "4. Run the application:"
echo "   - Desktop version: python main.py"
echo "   - Web version: python main_web.py"
echo ""
echo "For help, see README.md or visit: https://github.com/yourusername/canannounce"
