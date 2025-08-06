"""
Main Flask web application for Canvas announcements.
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from datetime import datetime, timedelta, timezone
import sys

# Fix imports to work with your project structure
# Use relative imports for modules within the canannounce package
from ..utils.announcement_utils import upload_file_to_course, calculate_trimmed_title
from ..core.course_utils import get_upcoming_assignments, get_canvas_courses, get_course_details
from ..utils.quiz_utils import get_next_quiz_question
from ..config.settings_manager import settings_manager

# Create Flask app
def create_app():
    # Use the templates in the web/templates directory
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

    # Create Flask app with proper template and static paths
    app = Flask(__name__,
                static_url_path='/static',
                static_folder=static_dir,
                template_folder=template_dir)

    # Enable debugging
    app.config['DEBUG'] = True

    # Load settings dynamically
    def get_config_value(key, default=None):
        return settings_manager.get_setting(key, default)

    @app.route('/')
    def index():
        # If no course_id provided, redirect to course selection
        if not request.args.get('course_id'):
            # Get courses for the selection screen
            courses = get_canvas_courses(get_config_value('canvas_token'), get_config_value('canvas_base_url'))
            return render_template('select_course.html', courses=courses)

        # Process course-specific view
        course_id = request.args.get('course_id')
        course_name = request.args.get('course_name', 'Unnamed Course')
        upcoming_assignments = get_upcoming_assignments(
            get_config_value('canvas_token'),
            get_config_value('canvas_base_url'),
            course_id
        )

        # Fetch course details if course_name is missing
        if course_name == 'Unnamed Course' and course_id:
            course_details = get_course_details(
                get_config_value('canvas_token'),
                get_config_value('canvas_base_url'),
                course_id
            )
            if course_details and 'name' in course_details:
                course_name = course_details['name']

        # Determine publish date - default to 5 minutes from now in CDT
        cdt = timezone(timedelta(hours=-5))  # CDT is UTC-5
        now_cdt = datetime.now(cdt)
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
            default_body += f"<p><b>No Assignments are due in the next {get_config_value('UPCOMING_ASSIGNMENT_DAYS', 30)} Days</b></p>\n\n"
            print("No upcoming assignments found, added message to body")

        # Calculate default title
        default_title = calculate_trimmed_title(course_name).replace('Slides from', 'Slides from today')

        # Fetch quiz question if enabled
        quiz_question = None
        if get_config_value('INCLUDE_QUIZ_QUESTION', True):
            quiz_question = get_next_quiz_question(course_id)
            if quiz_question:
                default_body += f"\n\n<p><b>{get_config_value('QUIZ_QUESTION_PROMPT', 'Practice Question')}:</b> {quiz_question}</p>"
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
                            now=get_config_value('ANNOUNCEMENT_NOW', False),
                            tinymce_api_key=get_config_value('TINYMCE_API_KEY'),
                            upcoming_assignments=upcoming_assignments,
                            quiz_question=quiz_question,
                            quiz_question_prompt=get_config_value('QUIZ_QUESTION_PROMPT', 'Practice Question'))

    @app.route('/settings')
    def settings():
        """Display the settings page."""
        message = request.args.get('message')
        message_type = request.args.get('message_type', 'success')

        # Get non-sensitive settings for user editing
        user_settings = settings_manager.get_non_sensitive_settings()
        # Get all settings for display purposes
        all_settings = settings_manager.get_all_settings()

        return render_template('settings.html',
                             settings=user_settings,
                             all_settings=all_settings,
                             message=message,
                             message_type=message_type)

    @app.route('/settings', methods=['POST'])
    def save_settings():
        """Save user settings."""
        try:
            if request.is_json:
                settings_data = request.get_json()
            else:
                # Handle form submission
                settings_data = {}
                for key in request.form:
                    value = request.form[key]
                    # Convert string values to appropriate types
                    if value.lower() in ['true', 'false']:
                        settings_data[key] = value.lower() == 'true'
                    elif value.isdigit():
                        settings_data[key] = int(value)
                    else:
                        settings_data[key] = value

            success = settings_manager.save_user_settings(settings_data)

            if request.is_json:
                return jsonify({'success': success})
            else:
                if success:
                    return redirect(url_for('settings', message='Settings saved successfully', message_type='success'))
                else:
                    return redirect(url_for('settings', message='Error saving settings', message_type='danger'))

        except Exception as e:
            print(f"Error saving settings: {e}")
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)})
            else:
                return redirect(url_for('settings', message=f'Error: {str(e)}', message_type='danger'))

    @app.route('/settings/reset', methods=['POST'])
    def reset_settings():
        """Reset user settings to defaults."""
        try:
            # Remove user settings file
            import os
            if os.path.exists(settings_manager.user_settings_file):
                os.remove(settings_manager.user_settings_file)

            # Reload settings
            settings_manager.load_settings()

            return jsonify({'success': True})
        except Exception as e:
            print(f"Error resetting settings: {e}")
            return jsonify({'success': False, 'error': str(e)})

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

        # Check if announcement title mentions attachment but no file uploaded
        if ('slides' in title.lower() or 'deck' in title.lower()) and ('file' not in request.files or request.files['file'].filename == ''):
            return jsonify({
                'warning': True,
                'message': 'Your announcement title mentions an attachment but no file was uploaded. Are you sure you want to proceed?'
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
            token=get_config_value('canvas_token'),
            base_url=get_config_value('canvas_base_url')
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
            token=get_config_value('canvas_token'),
            base_url=get_config_value('canvas_base_url')
        )

        return jsonify(result)

    # Add a route for getting courses via API
    @app.route('/api/courses', methods=['GET'])
    def api_courses():
        courses = get_canvas_courses(get_config_value('canvas_token'), get_config_value('canvas_base_url'))
        return jsonify(courses)

    return app

# Create the app instance
app = create_app()

# Add this block to handle running as a module with port argument
if __name__ == "__main__":
    # Get port from command line argument
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='127.0.0.1', port=port, debug=True)
