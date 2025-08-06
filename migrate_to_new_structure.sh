#!/usr/bin/env bash
# Script to help migrate from the old structure to the new structure

# Create necessary directories if they don't exist
mkdir -p src/canannounce/web/templates
mkdir -p src/canannounce/web/static
mkdir -p uploads

# Copy templates and static files
echo "Copying templates and static files..."
cp -r templates/* src/canannounce/web/templates/
cp -r static/* src/canannounce/web/static/

# Create placeholder to keep uploads directory in git
touch uploads/.gitkeep

echo "Migration complete! You can now run the application with:"
echo "python run.py"
