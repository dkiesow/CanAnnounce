#!/usr/bin/env python3
"""
Wrapper script to run the Flask app with proper package imports.
This script is designed to be run directly from a subprocess.
"""
import os
import sys
import importlib.util
from flask import Flask, render_template, request, jsonify, redirect, url_for
import datetime as dt
from datetime import timedelta, timezone
import pathlib
import requests  # Import requests for direct API calls

# Determine the project root directory (not just src)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '../..'))

# Add src to Python path
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import config from src/canannounce/config/local_settings.py
config_path = os.path.join(src_dir, 'canannounce', 'config', 'local_settings.py')
spec = importlib.util.spec_from_file_location('config_module', config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

# Extract variables from config
canvas_token = config.canvas_token
canvas_base_url = config.canvas_base_url
ANNOUNCEMENT_NOW = getattr(config, 'ANNOUNCEMENT_NOW', True)
TINYMCE_API_KEY = getattr(config, 'TINYMCE_API_KEY', '')
INCLUDE_QUIZ_QUESTION = getattr(config, 'INCLUDE_QUIZ_QUESTION', False)
QUIZ_QUESTION_PROMPT = getattr(config, 'QUIZ_QUESTION_PROMPT', 'Quiz Question')
UPCOMING_ASSIGNMENT_DAYS = getattr(config, 'UPCOMING_ASSIGNMENT_DAYS', 7)

# Now import utils from the new structure
from canannounce.utils.announcement_utils import *
from canannounce.utils.quiz_utils import *
from canannounce.core.course_utils import *

# Define a function to filter courses based on the original filtering rules
def filter_courses(courses):
    """Filter courses based on business rules."""
    print(f"Starting filtering with {len(courses)} courses")

    # Get current date to determine current semester
    current_date = dt.datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    # Determine current semester based on month
    if 1 <= current_month <= 5:
        current_semester = "Spring"
    elif 6 <= current_month <= 7:
        current_semester = "Summer"
    else:  # 8-12
        current_semester = "Fall"

    # Format strings to look for in course/term names
    current_year_str = str(current_year)
    semester_patterns = [
        # Full semester names
        f"{current_semester} {current_year}",
        f"{current_semester}{current_year}",
        # Abbreviations (SP, SU, FA)
        f"{current_semester[:2].upper()}{current_year}",
        f"{current_semester[:2].upper()}-{current_year}",
        f"{current_semester[:2].upper()} {current_year}",
        # Year-semester format
        f"{current_year}{current_semester[:2].upper()}",
        f"{current_year}-{current_semester[:2].upper()}",
        f"{current_year} {current_semester[:2].upper()}",
        # 2-digit year formats
        f"{current_semester} {str(current_year)[2:]}",
        f"{current_semester}{str(current_year)[2:]}",
        f"{current_semester[:2].upper()}{str(current_year)[2:]}",
        f"{str(current_year)[2:]}{current_semester[:2].upper()}",
        # Code format (like 2025FS for Fall 2025)
        f"{current_year}{current_semester[:2]}",
    ]

    print(f"Filtering for courses matching patterns: {semester_patterns}")

    filtered_courses = []
    for course in courses:
        # Skip courses without a name or ID
        if 'name' not in course or not course['name'] or 'id' not in course:
            print(f"Skipping course with no name or ID: {course}")
            continue

        course_name = course['name'].lower()
        print(f"Processing course: {course['name']}")

        # Check if the user has a teacher enrollment in this course
        is_teacher = False
        if 'enrollments' in course:
            for enrollment in course['enrollments']:
                if enrollment.get('type') in ['teacher', 'ta', 'designer'] and enrollment.get('enrollment_state') == 'active':
                    is_teacher = True
                    break

        if not is_teacher:
            print(f"Skipping course (not a teacher): {course['name']}")
            continue

        # Skip courses with "sandbox" in the name (case insensitive)
        if 'sandbox' in course_name:
            print(f"Filtering out sandbox course: {course['name']}")
            continue

        # Check if course is in current semester
        is_current_semester = False
        term_name = course.get('term', {}).get('name', '').lower()

        # Look for semester pattern matches in course name or term name
        for pattern in semester_patterns:
            pattern_lower = pattern.lower()
            if (pattern_lower in course_name or
                (term_name and pattern_lower in term_name)):
                is_current_semester = True
                break

        if not is_current_semester:
            print(f"Filtering out non-current semester course: {course['name']}")
            continue

        # If we got here, the course passes all filters
        filtered_courses.append(course)

    # Sort courses alphabetically by name
    filtered_courses.sort(key=lambda c: c.get('name', ''))
    print(f"Finished filtering, returned {len(filtered_courses)} courses")
    return filtered_courses

# Define a custom function to fetch upcoming assignments properly
def get_upcoming_assignments_fixed(token, base_url, course_id, days_ahead=60):
    """
    Improved version of get_upcoming_assignments that properly fetches and filters assignments.
    """
    headers = {'Authorization': f'Bearer {token}'}
    url = f"{base_url}/api/v1/courses/{course_id}/assignments"
    params = {'per_page': 100}

    # Calculate date range
    now = dt.datetime.now(timezone.utc)
    future_date = now + timedelta(days=days_ahead)

    print(f"DEBUG: Looking for assignments between {now.isoformat()} and {future_date.isoformat()}")

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            assignments = []
            all_assignments = response.json()
            print(f"DEBUG: Found {len(all_assignments)} total assignments")

            for assignment in all_assignments:
                due_at = assignment.get('due_at')
                if due_at:
                    try:
                        # Convert ISO format to datetime object
                        due_date = dt.datetime.fromisoformat(due_at.replace('Z', '+00:00'))
                        print(f"DEBUG: Checking assignment '{assignment['name']}' with due date {due_date.isoformat()}")

                        # Include assignments that are due in the future, within our days_ahead window
                        if now <= due_date <= future_date:
                            # Create a simplified version of the assignment object
                            formatted_assignment = {
                                'name': assignment['name'],
                                'due_at': due_date.strftime('%Y-%m-%d %H:%M'),
                                'due_at_formatted': due_date.strftime('%b %d, %Y'),
                                'points_possible': assignment.get('points_possible', 0),
                                'html_url': assignment.get('html_url', '')
                            }
                            assignments.append(formatted_assignment)
                            print(f"DEBUG: Including assignment '{assignment['name']}'")
                        else:
                            print(f"DEBUG: Skipping assignment '{assignment['name']}' - outside time window")
                    except ValueError as e:
                        print(f"DEBUG: Error parsing date for '{assignment['name']}': {str(e)}")

            return sorted(assignments, key=lambda x: x['due_at'])
        else:
            print(f"DEBUG: Error getting assignments: {response.status_code}")
            return []
    except Exception as e:
        print(f"DEBUG: Exception in get_upcoming_assignments_fixed: {str(e)}")
        return []

# Create Flask app
def create_app():
    # Use the templates at the project root
    template_dir = os.path.abspath(os.path.join(current_dir, '../../../templates'))
    static_dir = os.path.abspath(os.path.join(current_dir, '../../../static'))

    # Create Flask app with proper template and static paths
    app = Flask(__name__,
                static_url_path='/static',
                static_folder=static_dir,
                template_folder=template_dir)

    # Enable debugging
    app.config['DEBUG'] = True

    @app.route('/select_course')
    def select_course():
        # Get courses for the selection screen
        all_courses = get_canvas_courses(canvas_token, canvas_base_url)
        # Apply filtering rules
        filtered_courses = filter_courses(all_courses)
        return render_template('select_course.html', courses=filtered_courses)

    @app.route('/')
    def index():
        # If no course_id provided, redirect to course selection
        if not request.args.get('course_id'):
            return redirect(url_for('select_course'))

        # Process course-specific view
        course_id = request.args.get('course_id')
        course_name = request.args.get('course_name', 'Unnamed Course')

        # Pass UPCOMING_ASSIGNMENT_DAYS from config to get_upcoming_assignments
        upcoming_assignments = get_upcoming_assignments_fixed(
            canvas_token,
            canvas_base_url,
            course_id,
            days_ahead=UPCOMING_ASSIGNMENT_DAYS
        )

        # Add debug output for assignments
        print(f"DEBUG: UPCOMING_ASSIGNMENT_DAYS = {UPCOMING_ASSIGNMENT_DAYS}")
        print(f"DEBUG: Retrieved {len(upcoming_assignments) if upcoming_assignments else 0} upcoming assignments")
        if not upcoming_assignments:
            # Let's examine the raw assignments from Canvas
            print("DEBUG: Attempting direct API call to retrieve assignments")
            headers = {'Authorization': f'Bearer {canvas_token}'}
            url = f"{canvas_base_url}/api/v1/courses/{course_id}/assignments"
            params = {'per_page': 100}

            try:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    all_assignments = response.json()
                    print(f"DEBUG: Canvas API returned {len(all_assignments)} total assignments")
                    # Print the first few assignments for debugging
                    for i, assignment in enumerate(all_assignments[:3]):
                        print(f"DEBUG: Assignment {i+1}: Name={assignment.get('name')}, due_at={assignment.get('due_at')}")
                else:
                    print(f"DEBUG: Error retrieving assignments, status={response.status_code}")
            except Exception as e:
                print(f"DEBUG: Exception during API request: {str(e)}")

        # Fetch course details if course_name is missing
        if course_name == 'Unnamed Course' and course_id:
            course_details = get_course_details(canvas_token, canvas_base_url, course_id)
            if course_details and 'name' in course_details:
                course_name = course_details['name']

        # Determine publish date - default to 5 minutes from now in CDT
        cdt = timezone(timedelta(hours=-5))  # CDT is UTC-5
        now_cdt = dt.datetime.now(cdt)
        future_date_cdt = now_cdt + timedelta(minutes=5)
        # Format for datetime-local input
        default_publish_datetime = future_date_cdt.strftime('%Y-%m-%dT%H:%M')

        # Prepare default body text
        default_body = "<p><a href='[FILE_URL_PLACEHOLDER]'>Today's slides are here</a></p>\n\n<p>ENTER BODY TEXT</p>\n\n"

        # Debug output for assignments
        print(f"Upcoming assignments count: {len(upcoming_assignments) if upcoming_assignments else 0}")
        if upcoming_assignments:
            assignments_html = []
            for assignment in upcoming_assignments:
                # Get the formatted due date
                due_date = assignment['due_at_formatted'] if 'due_at_formatted' in assignment else assignment['due_at']

                # Create hyperlink if html_url is available, otherwise just use the name
                if 'html_url' in assignment and assignment['html_url']:
                    assignment_link = f'<a href="{assignment["html_url"]}" target="_blank">{assignment["name"]}</a>'
                else:
                    assignment_link = assignment['name']

                # Add the list item with hyperlinked assignment name
                assignments_html.append(f"<li>{assignment_link} (Due: {due_date})</li>")

            # Join all list items and add to the default body
            default_body += f"<p><b>Upcoming Assignments:</b></p>\n<ul>\n{''.join(assignments_html)}\n</ul>"
            print(f"Added hyperlinked assignments HTML")
        else:
            # Add message when no assignments are found
            default_body += f"<p><b>No Assignments are due in the next {UPCOMING_ASSIGNMENT_DAYS} Days</b></p>\n\n"
            print("No upcoming assignments found, added message to body")

        # Calculate default title
        default_title = calculate_trimmed_title(course_name).replace('Slides from', 'Slides from today')

        # Fetch quiz question if enabled
        quiz_question = None
        if INCLUDE_QUIZ_QUESTION:
            quiz_question = get_next_quiz_question(course_id)
            if quiz_question:
                default_body += f"\n\n<p><b>{QUIZ_QUESTION_PROMPT}:</b> {quiz_question}</p>"
                print(f"Added quiz question: {quiz_question[:100]}...")

        # Debug output of full default_body
        print(f"Full default_body content: {default_body}")

        # Render the modal template instead of select_course.html
        return render_template('modal.html',
                            course_id=course_id,
                            course_name=course_name,
                            default_title=default_title,
                            default_body=default_body,
                            default_publish_datetime=default_publish_datetime,
                            now=ANNOUNCEMENT_NOW,
                            tinymce_api_key=TINYMCE_API_KEY,
                            upcoming_assignments=upcoming_assignments,
                            quiz_question=quiz_question,
                            quiz_question_prompt=QUIZ_QUESTION_PROMPT)

    @app.route('/submit', methods=['POST'])
    def submit():
        """Handle form submissions from the announcement form."""
        # Process form data
        course_id = request.form.get('course_id')
        title = request.form.get('title', '')
        body = request.form.get('body', '')
        publish_date = request.form.get('publish_date', '')  # Note: form uses publish_date, not publish_at

        # Check for placeholder text as an additional server-side validation
        if 'ENTER BODY TEXT' in body and 'force_submit' not in request.form:
            return jsonify({
                'warning': True,
                'message': 'Your announcement still contains placeholder text. Are you sure you want to submit?'
            })

        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})

        # Process the upload using the existing function
        result = upload_file_to_course(
            course_id=course_id,
            title=title,
            body=body,
            file=file,
            publish_at=publish_date,  # Pass the publish_date to the function
            token=canvas_token,
            base_url=canvas_base_url
        )

        return jsonify(result)

    # Existing upload route remains as a backup
    @app.route('/upload', methods=['POST'])
    def upload():
        # Process form data
        course_id = request.form.get('course_id')
        title = request.form.get('title', '')
        body = request.form.get('body', '')
        publish_at = request.form.get('publish_at', '')

        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})

        # Process the upload
        result = upload_file_to_course(
            course_id=course_id,
            title=title,
            body=body,
            file=file,
            publish_at=publish_at,
            token=canvas_token,
            base_url=canvas_base_url
        )

        return jsonify(result)

    # Add a route for getting courses via API
    @app.route('/api/courses', methods=['GET'])
    def api_courses():
        courses = get_canvas_courses(canvas_token, canvas_base_url)
        # Apply filtering to courses
        filtered_courses = filter_courses(courses)
        return jsonify(filtered_courses)

    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    # Get port from command line argument
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='127.0.0.1', port=port, debug=True)
