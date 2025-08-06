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


def calculate_trimmed_title(course_name, max_length=50):
    """
    Generate a trimmed title for announcements based on course name.
    Extracts course code and adds today's date.

    Args:
        course_name (str): The full course name
        max_length (int): Maximum length for the title

    Returns:
        str: Formatted announcement title like "Slides from today JOURN-4734 8/06"
    """
    import re
    from datetime import datetime

    # Get today's date in (MM/DD/YY) format
    today = datetime.now()
    date_str = f"({today.month:02d}/{today.day:02d}/{str(today.year)[2:]})"

    # Extract course code from various formats
    course_code = None

    # Pattern 1: Extract from format like "2025FS-JOURN-4734-01"
    match = re.search(r'([A-Z]{3,5}-\d{4})', course_name)
    if match:
        course_code = match.group(1)
    else:
        # Pattern 2: Extract from format like "JOURN 4734" or "JOURN-4734"
        match = re.search(r'([A-Z]{3,5})\s*[-\s]\s*(\d{4})', course_name)
        if match:
            course_code = f"{match.group(1)}-{match.group(2)}"
        else:
            # Pattern 3: Fallback - try to extract any course-like pattern
            match = re.search(r'([A-Z]{3,5}\s*\d{3,4})', course_name)
            if match:
                course_code = match.group(1).replace(' ', '-')

    # If we couldn't extract a course code, use a cleaned version of the course name
    if not course_code:
        # Remove semester info and clean up
        clean_name = re.sub(r'\b(Fall|Spring|Summer)\s*\d{4}\b', '', course_name, flags=re.IGNORECASE)
        clean_name = re.sub(r'\b(FA|SP|SU)\s*\d{2,4}\b', '', clean_name, flags=re.IGNORECASE)
        clean_name = re.sub(r'^\d{4}[A-Z]{2}-', '', clean_name)  # Remove semester prefix like "2025FS-"
        clean_name = ' '.join(clean_name.split())
        course_code = clean_name[:20] if clean_name else "Course"

    # Create the title
    title = f"Slides from today {course_code} {date_str}"

    # Trim to max length if needed
    if len(title) > max_length:
        # Keep the important parts and truncate the course code if necessary
        base = f"Slides from today "
        suffix = f" {date_str}"
        available_length = max_length - len(base) - len(suffix) - 3  # -3 for "..."
        if available_length > 0:
            truncated_code = course_code[:available_length] + "..."
            title = f"{base}{truncated_code}{suffix}"
        else:
            title = title[:max_length-3] + "..."

    return title
