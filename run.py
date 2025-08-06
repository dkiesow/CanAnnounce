#!/usr/bin/env python3
"""
Top-level entry point script for running the Canvas Announcements application.
By default, launches the app in a PyQt5 modal window. Use --web flag to run as a web server.
"""

import sys
import os
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run Canvas Announcements application')
parser.add_argument('--web', action='store_true', help='Run as web server instead of PyQt5 window')
args = parser.parse_args()

# Ensure we can import the canannounce package
package_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, package_dir)

if args.web:
    # Run as traditional web server
    try:
        from canannounce.web.app import app

        # Print debug information about template locations
        print("\nDebug information:")
        print(f"Current working directory: {os.getcwd()}")
        template_path = os.path.join(os.getcwd(), 'templates')
        print(f"Root template path exists: {os.path.exists(template_path)}")
        src_template_path = os.path.join(os.getcwd(), 'src/canannounce/web/templates')
        print(f"Src template path exists: {os.path.exists(src_template_path)}")
        print(f"Flask app template folder: {app.template_folder}")
        print(f"Flask app template folder exists: {os.path.exists(app.template_folder)}")

        # Run the web server
        print("Starting web server mode...")
        app.run(debug=True)

    except ImportError as e:
        print(f"Error importing application modules: {e}")
        print("\nThis may be due to a missing dependency or incorrect project structure.")
        print("Make sure you've installed the required packages:")
        print("  pip install -r requirements.txt")
else:
    # Default: Run in PyQt5 modal window
    try:
        print("Starting PyQt5 modal window mode...")
        # Import the PyQt5 implementation
        from canannounce.main import run_pyqt_window

        # Run the application with the PyQt5 window
        run_pyqt_window()

    except ImportError as e:
        print(f"Error importing PyQt5 modules: {e}")
        print("\nThis may be due to missing PyQt5 dependencies.")
        print("Make sure you've installed the required packages:")
        print("  pip install -r requirements.txt")
        print("  pip install PyQt5==5.15.9 PyQtWebEngine==5.15.6")
