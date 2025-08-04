"""
Course-related utilities for Canvas API operations.
"""
import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict


def get_course_details(token, base_url, course_id):
    """
    Fetch details for a specific Canvas course by ID.

    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance.
        course_id (int or str): The Canvas course ID.

    Returns:
        dict: Course details if successful, None otherwise.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f"{base_url}/api/v1/courses/{course_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch course details. Status code: {response.status_code}")
        print(response.text)
        return None


def get_upcoming_assignments(token, base_url, course_id, days_ahead=60):
    """
    Fetch upcoming assignments for a Canvas course.

    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance.
        course_id (int or str): The Canvas course ID.
        days_ahead (int): Number of days to look ahead for assignments.

    Returns:
        list: List of upcoming assignments.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Calculate date range
    now = datetime.now(timezone.utc)
    future_date = now + timedelta(days=days_ahead)

    url = f"{base_url}/api/v1/courses/{course_id}/assignments"
    params = {
        'bucket': 'upcoming',
        'per_page': 100,
        'include[]': ['submission']
    }

    assignments = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            batch = response.json()
            for assignment in batch:
                due_at = assignment.get('due_at')
                if due_at:
                    try:
                        due_date = datetime.fromisoformat(due_at.replace('Z', '+00:00'))
                        if now <= due_date <= future_date:
                            assignments.append({
                                'name': assignment['name'],
                                'due_at': due_date.strftime('%Y-%m-%d %H:%M'),
                                'points_possible': assignment.get('points_possible', 0)
                            })
                    except ValueError:
                        continue

            # Check for pagination
            links = response.headers.get('Link', '')
            url = None
            for link in links.split(','):
                if 'rel="next"' in link:
                    url = link.split(';')[0].strip('<> ')
                    break
        else:
            print(f"Failed to fetch assignments. Status code: {response.status_code}")
            break

    return sorted(assignments, key=lambda x: x['due_at'])


def get_course_people(token, base_url, course_id):
    """
    Fetch a list of people in a Canvas course, including their roles and metadata.

    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance.
        course_id (int or str): The Canvas course ID.

    Returns:
        list: List of people if successful, empty list otherwise.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f"{base_url}/api/v1/courses/{course_id}/users"
    params = {
        'include[]': ['enrollments'],
        'per_page': 100
    }

    people = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            batch = response.json()
            people.extend(batch)

            # Check for pagination
            links = response.headers.get('Link', '')
            url = None
            for link in links.split(','):
                if 'rel="next"' in link:
                    url = link.split(';')[0].strip('<> ')
                    break
        else:
            print(f"Failed to fetch course people. Status code: {response.status_code}")
            break

    return people


def filter_courses_by_role(token, base_url, courses, role="teacher"):
    """
    Filter courses by user role.

    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance.
        courses (list): List of courses to filter.
        role (str): Role to filter by (teacher, student, ta, etc.).

    Returns:
        list: Filtered list of courses.
    """
    filtered_courses = []

    for course in courses:
        course_id = course.get('id')
        if not course_id:
            continue

        people = get_course_people(token, base_url, course_id)

        # Check if current user has the specified role
        for person in people:
            enrollments = person.get('enrollments', [])
            for enrollment in enrollments:
                if enrollment.get('role', '').lower() == role.lower():
                    filtered_courses.append(course)
                    break
            if course in filtered_courses:
                break

    return filtered_courses
