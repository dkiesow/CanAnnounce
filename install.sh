#!/bin/bash
# Quick install script for CanAnnounce

set -e

echo "🎯 CanAnnounce Quick Install"
echo "============================"

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "📍 Python version: $python_version"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"; then
    echo "❌ Python 3.8+ is required. Please upgrade Python."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install the package in development mode
echo "📥 Installing CanAnnounce..."
pip install -e .

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Run configuration setup: canannounce-setup"
echo "2. Start the application: canannounce"
echo ""
echo "📁 To activate this environment later:"
echo "   source venv/bin/activate"
