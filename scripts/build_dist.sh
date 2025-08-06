#!/bin/bash
# Build and package CanAnnounce for distribution

set -e

echo "📦 Building CanAnnounce Distribution Package"
echo "==========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Get the project root directory (parent of scripts directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Create source distribution
echo "📄 Building source distribution..."
python setup.py sdist

# Create wheel distribution
echo "🎡 Building wheel distribution..."
python setup.py bdist_wheel

echo ""
echo "✅ Distribution packages created:"
ls -la dist/

echo ""
echo "📤 To upload to PyPI:"
echo "pip install twine"
echo "twine upload dist/*"

echo ""
echo "🧪 To test installation locally:"
echo "pip install dist/canannounce-*.whl"
