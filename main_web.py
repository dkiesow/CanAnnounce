#!/usr/bin/env python3
"""
Web-only version of Can Announce that opens in your default browser
This version doesn't require PyQt5 and should work without dependency issues
"""

import requests
import subprocess
import os
import sys
import socket
import webbrowser
import time

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


if __name__ == '__main__':
    print("Starting Can Announce (Web Version)...")

    # Import Canvas token and base URL from config.py
    try:
        from config import canvas_token, canvas_base_url
    except ImportError:
        print("Error: config.py not found. Please create it from config_template.py")
        sys.exit(1)

    CANVAS_TOKEN = canvas_token
    CANVAS_BASE_URL = canvas_base_url

    # Test Canvas API connection
    print("Testing Canvas API connection...")
    test_canvas_api(CANVAS_TOKEN, CANVAS_BASE_URL)
    courses = get_canvas_courses(CANVAS_TOKEN, CANVAS_BASE_URL)

    # Dynamically find an available port for Flask
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    print(f"Starting Flask app on port {port}...")

    # Launch the Flask app
    python_executable = sys.executable
    flask_process = subprocess.Popen(
        [python_executable, "app.py", str(port)],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        env={**os.environ, "FLASK_ENV": "development"}
    )

    # Wait for Flask app to start
    print("Waiting for Flask app to initialize...")
    for attempt in range(10):
        try:
            response = requests.get(f"http://127.0.0.1:{port}/select_course")
            if response.status_code == 200:
                print("Flask app is ready!")
                break
        except requests.ConnectionError:
            time.sleep(1)
            print(f"  Attempt {attempt + 1}/10...")
    else:
        print("Flask app failed to start within 10 seconds.")
        flask_process.terminate()
        sys.exit(1)

    # Open in default web browser
    url = f"http://127.0.0.1:{port}/select_course"
    print(f"Opening Can Announce in your browser: {url}")
    webbrowser.open(url)

    print("\nCan Announce is now running!")
    print("- The app will open in your default web browser")
    print("- Close this terminal or press Ctrl+C to stop the app")
    print("- The app will automatically close after submitting an announcement")

    try:
        # Keep the script running
        flask_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        flask_process.terminate()
        flask_process.wait()
        print("Can Announce stopped.")
