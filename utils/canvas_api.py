"""
Canvas API utilities for authentication and basic operations.
"""
import requests


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
        list: List of courses if successful, empty list otherwise.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f'{base_url}/api/v1/courses'
    params = {
        'enrollment_state': 'active',
        'per_page': 100,
        'include[]': ['term', 'course_image']
    }

    courses = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            batch = response.json()
            courses.extend(batch)
            # Check for pagination
            links = response.headers.get('Link', '')
            url = None
            for link in links.split(','):
                if 'rel="next"' in link:
                    url = link.split(';')[0].strip('<> ')
                    break
        else:
            print(f'Failed to fetch courses. Status code: {response.status_code}')
            print(response.text)
            break

    return courses


def post_announcement(token, base_url, course_id, title, message, delayed_post_at=None):
    """
    Post an announcement to a Canvas course.

    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance.
        course_id (str): Course ID to post the announcement to.
        title (str): Announcement title.
        message (str): Announcement message body.
        delayed_post_at (str, optional): ISO datetime string for delayed posting.

    Returns:
        dict: Response data if successful, None otherwise.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f"{base_url}/api/v1/courses/{course_id}/discussion_topics"
    payload = {
        'title': title,
        'message': message,
        'is_announcement': True
    }
    if delayed_post_at:
        payload['delayed_post_at'] = delayed_post_at

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in (200, 201):
        return response.json()
    else:
        print(f'Failed to post announcement. Status code: {response.status_code}')
        print(response.text)
        return None
