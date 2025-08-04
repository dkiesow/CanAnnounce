import requests
import os
import datetime

def upload_file_to_course(token, base_url, course_id, file_path):
    """
    Upload a file to a Canvas course and return the file download URL.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    filename = os.path.basename(file_path)
    # Step 1: Start the file upload
    url = f"{base_url}/api/v1/courses/{course_id}/files"
    params = {
        'name': filename,
        'parent_folder_path': '/uploaded_announcements',
        'overwrite': True
    }
    with open(file_path, 'rb') as f:
        # Step 2: Get upload URL and params
        init_resp = requests.post(url, headers=headers, data=params)
        if init_resp.status_code != 200:
            return None
        upload_info = init_resp.json()
        upload_url = upload_info['upload_url']
        upload_params = upload_info['upload_params']
        # Step 3: Upload the file
        files = {'file': (filename, f)}
        upload_resp = requests.post(upload_url, data=upload_params, files=files)
        if upload_resp.status_code not in (200, 201, 302):
            return None
        # Step 4: Get file download URL
        if upload_resp.status_code == 302:
            # Some Canvas instances redirect after upload
            location = upload_resp.headers['Location']
            file_info = requests.get(location, headers=headers).json()
        else:
            file_info = upload_resp.json()
        return file_info.get('url')

def calculate_trimmed_title(course_name):
    """
    Generate a trimmed course title with the format:
    "<Trimmed Course Name> Slides from <Day of Week> <Date>"
    """
    # Get the current date
    now = datetime.datetime.now()
    day_of_week = now.strftime('%A')
    month_day_year = now.strftime('%m/%d')  # Ensure consistent MM/DD format

    # Trim course name: remove up to and including first hyphen, and remove from last hyphen to end
    trimmed_course_name = course_name
    if '-' in trimmed_course_name:
        # Remove up to and including first hyphen
        trimmed_course_name = trimmed_course_name.split('-', 1)[-1].strip()
    if '-' in trimmed_course_name:
        # Remove from last hyphen to end
        trimmed_course_name = trimmed_course_name.rsplit('-', 1)[0].strip()

    # Format the title
    return f"{trimmed_course_name} Slides from {day_of_week} {month_day_year}"
