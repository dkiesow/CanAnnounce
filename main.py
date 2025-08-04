import requests
import subprocess
import os
import sys
import socket
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

def test_canvas_api(token, base_url):
    """
    Test Canvas API authentication by fetching the current user's profile.
    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance (e.g., https://canvas.instructure.com)
    Returns:
        dict: User profile if successful, None otherwise.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f'{base_url}/api/v1/users/self/profile'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print('Authentication successful!')
        print('User profile:')
        print(response.json())
        return response.json()
    else:
        print(f'Authentication failed. Status code: {response.status_code}')
        print(response.text)
        return None


def get_canvas_courses(token, base_url):
    """
    Fetch a list of courses the user has access to.
    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance.
    Returns:
        list: List of courses if successful, None otherwise.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'enrollment_state': 'active',
        'state': 'available'
    }
    url = f'{base_url}/api/v1/courses'
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        courses = response.json()
        print('Courses:')
        for course in courses:
            print(f"- {course.get('name', 'Unnamed Course')} (ID: {course.get('id')})")
        return courses
    else:
        print(f'Failed to fetch courses. Status code: {response.status_code}')
        print(response.text)
        return None


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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Import Canvas token and base URL from config.py
    from config import canvas_token, canvas_base_url
    CANVAS_TOKEN = canvas_token
    CANVAS_BASE_URL = canvas_base_url
    test_canvas_api(CANVAS_TOKEN, CANVAS_BASE_URL)
    courses = get_canvas_courses(CANVAS_TOKEN, CANVAS_BASE_URL)

    # Dynamically find an available port for Flask
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    # Launch the Flask app for the modal UI
    # Ensure we use the same Python interpreter that's currently running
    python_executable = sys.executable
    flask_process = subprocess.Popen(
        [python_executable, "app.py", str(port)],  # Pass the port as an argument
        cwd=os.path.dirname(os.path.abspath(__file__)),
        env={**os.environ, "FLASK_ENV": "development"}
    )

    # Ensure Flask app is fully initialized before accessing the route
    import time
    for _ in range(10):  # Retry for up to 10 seconds
        try:
            response = requests.get(f"http://127.0.0.1:{port}/select_course")
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
        sys.exit(app.exec_())
    finally:
        flask_process.terminate()
