"""
Utilities for interacting with Canvas courses and assignments.
"""
import requests
import datetime
from collections import defaultdict
from datetime import timezone, timedelta
from ..config import UPCOMING_ASSIGNMENT_DAYS


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


def get_course_people(token, base_url, course_id):
    """
    Fetch a list of people in a Canvas course, including their roles and metadata.
    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance.
        course_id (int or str): The Canvas course ID.
    Returns:
        list: List of people if successful, None otherwise.
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
            # Check for pagination Link header
            links = response.links if hasattr(response, 'links') else {}
            url = links.get('next', {}).get('url')
        else:
            print(f"Failed to fetch course people. Status code: {response.status_code}")
            return None
    return people


def get_canvas_courses(token, base_url, filter_term=None):
    """
    Fetch a list of active Canvas courses for the authenticated user.
    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance.
        filter_term (str, optional): If provided, only return courses containing this term in their name.
    Returns:
        list: List of active courses where the user is a teacher in the current semester.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f"{base_url}/api/v1/courses"
    params = {
        'enrollment_state': 'active',
        'include[]': ['term', 'enrollments'],  # Include term and enrollment information
        'per_page': 100
    }

    # Get current date to determine current semester
    current_date = datetime.datetime.now()
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

    courses = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            batch = response.json()
            # Filter out courses without a name or ID
            valid_courses = [c for c in batch if c.get('name') and c.get('id')]

            # Filter for courses where the user is a teacher and in current semester
            filtered_courses = []
            for course in valid_courses:
                # Check if the user has a teacher enrollment in this course
                is_teacher = False
                if 'enrollments' in course:
                    for enrollment in course['enrollments']:
                        if enrollment.get('type') in ['teacher', 'ta', 'designer'] and enrollment.get('enrollment_state') == 'active':
                            is_teacher = True
                            break

                if not is_teacher:
                    continue

                # Skip courses with "sandbox" in the name (case insensitive)
                course_name = course.get('name', '').lower()
                if 'sandbox' in course_name:
                    continue

                # Check if course is in current semester
                is_current_semester = False
                term_name = course.get('term', {}).get('name', '')

                # Look for semester pattern matches in course name or term name
                for pattern in semester_patterns:
                    pattern_lower = pattern.lower()
                    if (pattern_lower in course_name.lower() or
                        (term_name and pattern_lower in term_name.lower())):
                        is_current_semester = True
                        break

                # If no direct semester pattern match, try matching current year with certain course codes
                if not is_current_semester and current_year_str in course_name:
                    # Check for course codes that typically include semester indicators like JOUR-4734-01
                    if any(code in course_name for code in ['-01', '-02', '-03', '-1', '-2', '-3', '-section']):
                        is_current_semester = True

                if not is_current_semester:
                    continue

                # Format course name for better display
                if term_name and term_name.lower() not in course_name.lower():
                    course['display_name'] = f"{course['name']} ({term_name})"
                else:
                    course['display_name'] = course['name']

                filtered_courses.append(course)

            courses.extend(filtered_courses)
            # Check for pagination Link header
            links = response.links if hasattr(response, 'links') else {}
            url = links.get('next', {}).get('url')
        else:
            print(f"Failed to fetch courses. Status code: {response.status_code}")
            return []

    # Sort courses by name
    courses.sort(key=lambda c: c.get('name', ''))

    return courses


def get_upcoming_assignments(token, base_url, course_id, days=None):
    """
    Fetch upcoming assignments for a Canvas course.
    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance.
        course_id (int or str): The Canvas course ID.
        days (int, optional): Number of days into the future to look for assignments.
                             If None, uses the UPCOMING_ASSIGNMENT_DAYS from config.
    Returns:
        list: List of upcoming assignments with due dates, sorted by due date.
    """
    # Use config value if days parameter is not provided
    if days is None:
        days = UPCOMING_ASSIGNMENT_DAYS

    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f"{base_url}/api/v1/courses/{course_id}/assignments"

    # Get current time and time in the future
    now = datetime.datetime.now(timezone.utc)
    future = now + timedelta(days=days)

    # Log the time window being used
    print(f"Looking for assignments between {now} and {future} ({days} days ahead)")

    assignments = []
    params = {'per_page': 100}

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            batch = response.json()
            for assignment in batch:
                # Only include assignments with due dates in the future
                if assignment.get('due_at'):
                    try:
                        due_date = datetime.datetime.fromisoformat(assignment['due_at'].replace('Z', '+00:00'))
                        if now <= due_date <= future:
                            assignment['due_at_formatted'] = due_date.strftime('%b %d, %Y')
                            assignments.append(assignment)
                    except (ValueError, TypeError) as e:
                        print(f"Error parsing due date for assignment {assignment.get('name')}: {e}")
                # Assignments with no due dates are now excluded

            # Check for pagination
            links = response.links if hasattr(response, 'links') else {}
            url = links.get('next', {}).get('url')
        else:
            print(f"Failed to fetch assignments. Status code: {response.status_code}")
            return []

    # Sort assignments by due date
    assignments.sort(key=lambda x: x['due_at'])

    # No need to add no_due_date_assignments since we're excluding them
    return assignments
