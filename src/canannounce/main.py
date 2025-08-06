#!/usr/bin/env python3
"""
Command line entry point for the CanAnnounce application.
Supports both CLI and PyQt modal window modes.
"""

import sys
import argparse
import os
import socket
import subprocess
import time
import requests
from canannounce.core.course_utils import get_canvas_courses
from canannounce.utils.announcement_utils import upload_file_to_course
from canannounce.config import canvas_token, canvas_base_url

# PyQt imports - only imported when needed
def import_pyqt():
    global QApplication, QMainWindow, QWebEngineView, QUrl
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtCore import QUrl
    return QApplication, QMainWindow, QWebEngineView, QUrl

def run_pyqt_window():
    """
    Run the application in a PyQt modal window.
    This function starts a Flask server and displays it in a PyQt window.
    """
    # Import PyQt modules only when needed
    QApplication, QMainWindow, QWebEngineView, QUrl = import_pyqt()

    # Define FlaskWindow class after PyQt modules are imported
    class FlaskWindow(QMainWindow):
        def __init__(self, url):
            super().__init__()
            self.setWindowTitle("Canvas Announcement Entry")
            # Increase window size and center it better on screen
            self.setGeometry(50, 50, 1200, 900)  # x, y, width, height

            self.browser = QWebEngineView()
            self.browser.setUrl(QUrl(url))

            # Remove scroll bars from the web view
            self.browser.page().settings().setAttribute(
                self.browser.page().settings().WebAttribute.ShowScrollBars, False
            )

            # Monitor for shutdown signal from the web page
            self.browser.page().titleChanged.connect(self.check_for_shutdown)

            self.setCentralWidget(self.browser)

        def check_for_shutdown(self, title):
            """Check if the web page is requesting shutdown"""
            if title == "SHUTDOWN_REQUESTED":
                print("Shutdown requested by web page")
                self.close()

        def closeEvent(self, event):
            """Handle window close event to ensure proper cleanup"""
            print("Closing application...")
            event.accept()

    # Test Canvas API before launching
    from canannounce.utils.announcement_utils import test_canvas_api
    test_canvas_api(canvas_token, canvas_base_url)

    # Dynamically find an available port for Flask
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    # Get path to the web app wrapper script that handles imports properly
    app_wrapper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'web', 'run_app.py'))

    # Launch the Flask app for the modal UI using the wrapper script
    python_executable = sys.executable
    flask_process = subprocess.Popen(
        [python_executable, app_wrapper_path, str(port)],
        env={**os.environ, "FLASK_ENV": "development"}
    )

    # Ensure Flask app is fully initialized before accessing the route
    for _ in range(10):  # Retry for up to 10 seconds
        try:
            response = requests.get(f"http://127.0.0.1:{port}/")
            if response.status_code == 200:
                print("Flask app is ready.")
                break
        except requests.ConnectionError:
            time.sleep(1)
    else:
        print("Flask app failed to start.")
        flask_process.terminate()
        sys.exit(1)

    # Open the Flask app in a PyQt5 modal window
    app = QApplication(sys.argv)
    url = f"http://127.0.0.1:{port}/select_course"  # Start with the course selection screen
    window = FlaskWindow(url)
    window.show()

    try:
        return_code = app.exec_()
        return return_code
    finally:
        # Ensure the Flask process is terminated when the PyQt window is closed
        flask_process.terminate()
        print("Flask server terminated.")

def main():
    parser = argparse.ArgumentParser(description='Canvas Announcement Creator')
    parser.add_argument('--course-id', type=str, help='Canvas Course ID')
    parser.add_argument('--title', type=str, help='Announcement title')
    parser.add_argument('--body', type=str, help='Announcement body text')
    parser.add_argument('--file', type=str, help='File path to upload')
    parser.add_argument('--publish-at', type=str, help='When to publish (ISO format)')
    parser.add_argument('--list-courses', action='store_true', help='List available courses')
    parser.add_argument('--ui', action='store_true', help='Run with PyQt user interface')

    args = parser.parse_args()

    # Run PyQt window if requested
    if args.ui:
        return run_pyqt_window()

    # List courses if requested
    if args.list_courses:
        courses = get_canvas_courses(canvas_token, canvas_base_url)
        if not courses:
            print("No courses found or unable to fetch courses.")
            return 1

        print("\nAvailable Courses:")
        print("-" * 80)
        for i, course in enumerate(courses, 1):
            print(f"{i}. {course.get('name', 'Unnamed')} (ID: {course.get('id')})")
        print("-" * 80)
        return 0

    # Check required arguments for file upload
    if args.course_id and args.title and args.body and args.file:
        with open(args.file, 'rb') as file:
            result = upload_file_to_course(
                course_id=args.course_id,
                title=args.title,
                body=args.body,
                file=file,
                publish_at=args.publish_at,
                token=canvas_token,
                base_url=canvas_base_url
            )

        if result.get('success'):
            print(f"Success: {result.get('message')}")
            print(f"Announcement ID: {result.get('announcement_id')}")
            print(f"File URL: {result.get('file_url')}")
            return 0
        else:
            print(f"Error: {result.get('message')}")
            return 1
    else:
        if not args.list_courses:
            parser.print_help()
            print("\nError: Missing required arguments for announcement creation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
