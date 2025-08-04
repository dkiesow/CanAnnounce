from flask import Flask, render_template, request, jsonify
import os
from announcement_utils import upload_file_to_course, calculate_trimmed_title
from course_utils import get_upcoming_assignments, get_canvas_courses, get_course_details
from config import canvas_token, canvas_base_url, ANNOUNCEMENT_PUBLISH, TINYMCE_API_KEY
from datetime import datetime, timedelta, timezone
import requests
import sys

# Ensure Flask serves the static folder correctly
app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

@app.route('/')
def index():
    course_id = request.args.get('course_id', '')
    course_name = request.args.get('course_name', 'Unnamed Course')
    upcoming_assignments = get_upcoming_assignments(canvas_token, canvas_base_url, course_id)

    # Log a warning if course_name is missing
    if course_name == 'Unnamed Course':
        print("Warning: course_name is missing. Ensure it is passed as a query parameter.")

    # Fetch course details if course_name is missing
    if course_name == 'Unnamed Course' and course_id:
        course_details = get_course_details(canvas_token, canvas_base_url, course_id)
        if course_details and 'name' in course_details:
            course_name = course_details['name']
        else:
            print("Warning: Failed to fetch course name from Canvas API.")

    # Determine publish date - default to 5 minutes from now in CDT
    cdt = timezone(timedelta(hours=-5))  # CDT is UTC-5
    now_cdt = datetime.now(cdt)
    future_date_cdt = now_cdt + timedelta(minutes=5)
    # Format for datetime-local input (browser expects local time without timezone info)
    default_publish_datetime = future_date_cdt.strftime('%Y-%m-%dT%H:%M')

    # Prepare default body text
    default_body = "<p><a href='[FILE_URL_PLACEHOLDER]'>Today's slides are here</a></p>\n\n<p>ENTER BODY TEXT</p>\n\n"
    if upcoming_assignments:
        assignments_html = '\n'.join(
            [f"<li>{assignment['name']} (Due: {assignment['due_at']})</li>" for assignment in upcoming_assignments]
        )
        default_body += f"<p><b>Upcoming Assignments:</b></p>\n<ul>\n{assignments_html}\n</ul>"

    # Use the utility function to calculate the default title
    default_title = calculate_trimmed_title(course_name).replace('Slides from', 'Slides from today')

    return render_template('modal.html', course_name=course_name, publish_date=None, default_body=default_body, default_title=default_title, tinymce_api_key=TINYMCE_API_KEY, default_publish_datetime=default_publish_datetime)

@app.route('/submit', methods=['POST'])
def submit_announcement():
    try:
        data = request.form
        title = data.get('title')
        body = data.get('body')
        file = request.files.get('file')
        course_id = data.get('course_id')
        force_submit = data.get('force_submit', 'false').lower() == 'true'

        if 'ENTER BODY TEXT' in body:
            return jsonify({'error': 'Please replace the placeholder text before submitting.'}), 400

        file_url = None
        if file and file.filename:
            # Create uploads directory if it doesn't exist
            uploads_dir = 'uploads'
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)

            file_path = os.path.join(uploads_dir, file.filename)
            file.save(file_path)
            file_url = upload_file_to_course(canvas_token, canvas_base_url, course_id, file_path)

            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)

        # Handle file URL replacement or removal
        if file_url:
            # Replace placeholder with actual file URL
            body = body.replace('[FILE_URL_PLACEHOLDER]', file_url)
        else:
            # No file uploaded - check if title mentions slides/deck
            import re
            if re.search(r'\b(slides?|decks?)\b', title, re.IGNORECASE) and not force_submit:
                return jsonify({
                    'warning': True,
                    'message': 'Your announcement title mentions an attachment but no file was uploaded. Are you sure you want to proceed?'
                }), 200

            # Remove the paragraph containing the file placeholder
            body = re.sub(r'<p><a href=\'\[FILE_URL_PLACEHOLDER\]\'>Today\'s slides are here</a></p>\s*', '', body)
            # Also handle double quotes version just in case
            body = re.sub(r'<p><a href="\[FILE_URL_PLACEHOLDER\]">Today\'s slides are here</a></p>\s*', '', body)

        # Determine if the announcement should be published immediately or scheduled
        user_publish_date = data.get('publish_date')
        delayed_post_at = None

        if user_publish_date:
            # User selected a specific date/time (assumed to be in CDT)
            try:
                # Parse the datetime-local input (YYYY-MM-DDTHH:MM)
                user_datetime = datetime.fromisoformat(user_publish_date)
                # Treat the input as CDT (UTC-5) and convert to UTC for Canvas API
                cdt = timezone(timedelta(hours=-5))
                user_datetime_cdt = user_datetime.replace(tzinfo=cdt)
                user_datetime_utc = user_datetime_cdt.astimezone(timezone.utc)
                delayed_post_at = user_datetime_utc.isoformat()
            except ValueError:
                return jsonify({'error': 'Invalid publish date format.'}), 400
        elif not ANNOUNCEMENT_PUBLISH:
            # Fallback to 30 days in future if no date selected and immediate publish is disabled
            delayed_post_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

        # Logic to post the announcement to Canvas
        headers = {
            'Authorization': f'Bearer {canvas_token}'
        }
        url = f"{canvas_base_url}/api/v1/courses/{course_id}/discussion_topics"
        payload = {
            'title': title,
            'message': body,
            'is_announcement': True
        }
        if delayed_post_at:
            payload['delayed_post_at'] = delayed_post_at

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in (200, 201):
            # Schedule app shutdown after successful submission
            def shutdown_server():
                import threading
                import time
                def delayed_shutdown():
                    time.sleep(2)  # Give time for response to be sent
                    try:
                        # Gracefully shutdown Flask
                        func = request.environ.get('werkzeug.server.shutdown')
                        if func is None:
                            # Fallback for different Flask/Werkzeug versions
                            os.kill(os.getpid(), 9)
                        else:
                            func()
                    except Exception:
                        # Force exit if graceful shutdown fails
                        os._exit(0)
                thread = threading.Thread(target=delayed_shutdown)
                thread.daemon = True
                thread.start()

            shutdown_server()
            return jsonify({'success': True, 'message': 'Announcement submitted successfully!', 'shutdown': True})
        else:
            return jsonify({'error': 'Failed to submit announcement.', 'details': response.text}), 500

    except Exception as e:
        # Return JSON error response instead of HTML error page
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/select_course')
def select_course():
    # Fetch courses using the Canvas API
    courses = get_canvas_courses(canvas_token, canvas_base_url)

    # Ensure filtering logic completes before rendering the template
    if not courses:
        print("No courses available after filtering.")
        return render_template('select_course.html', courses=[]), 200

    # Log the filtered courses for debugging
    print("Filtered courses for selection:")
    for course in courses:
        print(f"- {course.get('name', 'Unnamed Course')} (ID: {course.get('id')})")

    # Render the course selection template with the filtered courses
    return render_template('select_course.html', courses=courses)

@app.route('/course_selected', methods=['POST'])
def course_selected():
    course_id = request.form.get('course_id')
    course_name = request.form.get('course_name', 'Unnamed Course')

    # Debugging: Log course_name and course_id
    print(f"Debug: Received course_id={course_id}, course_name={course_name}")
    print(f"Debug: TinyMCE API Key being passed: {TINYMCE_API_KEY}")

    # Get upcoming assignments for this course
    upcoming_assignments = get_upcoming_assignments(canvas_token, canvas_base_url, course_id)

    # Determine publish date - default to 5 minutes from now in CDT
    cdt = timezone(timedelta(hours=-5))  # CDT is UTC-5
    now_cdt = datetime.now(cdt)
    future_date_cdt = now_cdt + timedelta(minutes=5)
    # Format for datetime-local input (browser expects local time without timezone info)
    default_publish_datetime = future_date_cdt.strftime('%Y-%m-%dT%H:%M')

    # Prepare default body text
    default_body = "<p><a href='[FILE_URL_PLACEHOLDER]'>Today's slides are here</a></p>\n\n<p>ENTER BODY TEXT</p>\n\n"
    if upcoming_assignments:
        assignments_html = '\n'.join(
            [f"<li>{assignment['name']} (Due: {assignment['due_at']})</li>" for assignment in upcoming_assignments]
        )
        default_body += f"<p><b>Upcoming Assignments:</b></p>\n<ul>\n{assignments_html}\n</ul>"

    # Use the utility function to calculate the default title with proper trimming
    default_title = calculate_trimmed_title(course_name)

    # Redirect to the announcement creation screen
    return render_template(
        'modal.html',
        course_name=course_name,
        course_id=course_id,
        publish_date=None,
        default_body=default_body,
        default_title=default_title,
        tinymce_api_key=TINYMCE_API_KEY,
        default_publish_datetime=default_publish_datetime
    )

@app.route('/debug_static')
def debug_static():
    return app.send_static_file('styles.css')

@app.route('/debug_courses')
def debug_courses():
    courses = get_canvas_courses(canvas_token, canvas_base_url)
    if not courses:
        return jsonify({'error': 'No courses fetched from Canvas API'}), 500

    filtered_courses = filter_courses_by_role(canvas_token, canvas_base_url, courses, role="teacher")
    if not filtered_courses:
        return jsonify({'error': 'No courses available after filtering by role'}), 500

    return jsonify({'courses': filtered_courses}), 200

if __name__ == '__main__':
    import socket

    # Check if port is passed as command line argument
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        # Dynamically find an available port if no argument provided
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]

    app.run(debug=True, port=port)
