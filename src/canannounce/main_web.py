#!/usr/bin/env python3
"""
Web application entry point for the CanAnnounce application.
"""

import argparse
import sys
import os

# When run directly, use correct import based on how the file is being executed
if __name__ == "__main__":
    # If we're running this file directly, make sure the package is importable
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import app after potentially adjusting the path
from canannounce.web.app import app


def main():
    parser = argparse.ArgumentParser(description='Canvas Announcement Web Interface')
    parser.add_argument('--host', default='127.0.0.1', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')

    args = parser.parse_args()

    # Run the Flask application
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


if __name__ == "__main__":
    main()
