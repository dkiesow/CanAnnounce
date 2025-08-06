"""
Utilities for creating and managing Canvas announcements.
"""
import requests
import os
import datetime


def test_canvas_api(token, base_url):
    """
    Test Canvas API authentication by fetching the current user's profile.

    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance.

    Returns:
        dict: User profile if successful, None otherwise.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f'{base_url}/api/v1/users/self/profile'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def upload_file_to_course(course_id, title, body, file, publish_at=None, token=None, base_url=None):
    """
    Upload a file to a Canvas course and create an announcement with the file URL.

    Args:
        course_id (str): Canvas course ID
        title (str): Announcement title
        body (str): Announcement body text (HTML)
        file (FileStorage): Uploaded file object from Flask
        publish_at (str, optional): When to publish the announcement (ISO format)
        token (str): Canvas API token
        base_url (str): Canvas instance base URL

    Returns:
        dict: Result with success flag and message
    """
    if not token or not base_url:
        return {'success': False, 'message': 'Missing API credentials'}

    headers = {
        'Authorization': f'Bearer {token}'
    }

    try:
        # Step 1: Upload the file to Canvas
        filename = file.filename

        # Start the file upload process
        url = f"{base_url}/api/v1/courses/{course_id}/files"
        params = {
            'name': filename,
            'parent_folder_path': '/uploaded_announcements',
            'overwrite': True
        }

        # Get upload URL and parameters
        init_resp = requests.post(url, headers=headers, params=params)
        if init_resp.status_code != 200:
            return {'success': False, 'message': f'Failed to initialize file upload: {init_resp.text}'}

        upload_info = init_resp.json()
        upload_url = upload_info.get('upload_url')
        upload_params = upload_info.get('upload_params', {})

        # Upload the file
        files = {'file': (filename, file)}
        upload_resp = requests.post(upload_url, data=upload_params, files=files)

        if upload_resp.status_code not in (200, 201, 302):
            return {'success': False, 'message': f'Failed to upload file: {upload_resp.text}'}

        # Get file URL
        if upload_resp.status_code == 302:
            # Follow redirect to get file info
            location = upload_resp.headers.get('Location')
            file_info = requests.get(location, headers=headers).json()
        else:
            file_info = upload_resp.json()

        file_url = file_info.get('url')

        if not file_url:
            return {'success': False, 'message': 'Failed to get file URL'}

        # Step 2: Replace placeholder in the body with actual file URL
        body = body.replace('[FILE_URL_PLACEHOLDER]', file_url)

        # Step 3: Create the announcement
        announcement_url = f"{base_url}/api/v1/courses/{course_id}/discussion_topics"
        announcement_data = {
            'title': title,
            'message': body,
            'is_announcement': True,
            'published': True
        }

        # Add delayed posting if specified
        if publish_at:
            try:
                # Parse the datetime and convert to ISO format
                announcement_data['delayed_post_at'] = publish_at
            except ValueError:
                return {'success': False, 'message': 'Invalid publish date format'}

        # Create the announcement
        announcement_resp = requests.post(
            announcement_url,
            headers=headers,
            json=announcement_data
        )

        if announcement_resp.status_code != 200:
            return {'success': False, 'message': f'Failed to create announcement: {announcement_resp.text}'}

        announcement_info = announcement_resp.json()

        return {
            'success': True,
            'message': 'Announcement created successfully',
            'announcement_id': announcement_info.get('id'),
            'file_url': file_url
        }

    except Exception as e:
        return {'success': False, 'message': f'Error: {str(e)}'}


def calculate_trimmed_title(course_name):
    """
    Generate a trimmed course title with the format:
    "<Trimmed Course Name> Slides from <Day of Week> <Date>"

    Args:
        course_name (str): Full course name

    Returns:
        str: Formatted title string
    """
    # Get the current date
    now = datetime.datetime.now()
    day_of_week = now.strftime('%A')
    month_day = now.strftime('%m/%d')  # MM/DD format

    # Trim the course name if it's too long
    trimmed_name = course_name
    if len(course_name) > 30:
        # Find a good breaking point
        space_index = course_name.rfind(' ', 0, 30)
        if space_index > 0:
            trimmed_name = course_name[:space_index]
        else:
            trimmed_name = course_name[:27] + '...'

    return f"{trimmed_name} Slides from {day_of_week} {month_day}"
