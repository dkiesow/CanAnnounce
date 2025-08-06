import requests
import datetime
from collections import defaultdict
from datetime import timezone, timedelta

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
            # Handle pagination
            if 'next' in response.links:
                url = response.links['next']['url']
                params = None  # Only needed for first request
            else:
                url = None
        else:
            print(f"Failed to fetch people. Status code: {response.status_code}")
            print(response.text)
            return None
    return people

def get_course_assignments(token, base_url, course_id):
    """
    Fetch all assignments for a Canvas course.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f"{base_url}/api/v1/courses/{course_id}/assignments"
    params = {'per_page': 100}
    assignments = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            batch = response.json()
            assignments.extend(batch)
            if 'next' in response.links:
                url = response.links['next']['url']
                params = None
            else:
                url = None
        else:
            print(f"Failed to fetch assignments. Status code: {response.status_code}")
            print(response.text)
            return None
    return assignments

def get_upcoming_assignments(token, base_url, course_id):
    """
    Fetch upcoming assignments for a Canvas course within a specified number of days.
    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance.
        course_id (int or str): The Canvas course ID.
    Returns:
        list: List of upcoming assignments with their names and due dates.
    """
    from config import UPCOMING_ASSIGNMENT_DAYS

    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f"{base_url}/api/v1/courses/{course_id}/assignments"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch assignments. Status code: {response.status_code}")
        print(response.text)
        return []

    assignments = response.json()
    # Define CDT timezone (UTC-5 hours)
    cdt = timezone(timedelta(hours=-5))

    now = datetime.datetime.now(datetime.timezone.utc)  # Make 'now' timezone-aware
    upcoming = []
    for assignment in assignments:
        due_at = assignment.get('due_at')
        if due_at:
            due_date = datetime.datetime.fromisoformat(due_at.replace('Z', '+00:00')).astimezone(cdt)
            if now <= due_date <= now + datetime.timedelta(days=UPCOMING_ASSIGNMENT_DAYS):
                # Capitalize the day of the week and format the date
                formatted_due_date = due_date.strftime('%A %m/%d %I:%M %p').replace('am', 'a.m.').replace('pm', 'p.m.')

                # Create Canvas URL for the assignment
                assignment_id = assignment.get('id')
                assignment_name = assignment.get('name', 'Unnamed Assignment')
                canvas_assignment_url = f"{base_url}/courses/{course_id}/assignments/{assignment_id}"

                upcoming.append({
                    'name': f'<a href="{canvas_assignment_url}" target="_blank">{assignment_name}</a>',
                    'due_at': formatted_due_date
                })
    return upcoming

def print_course_people(token, base_url, course_id):
    """
    Print a list of people in the course with their roles and metadata.
    """
    people = get_course_people(token, base_url, course_id)
    if not people:
        print("No people found or failed to fetch people.")
        return
    print(f"People in course {course_id}:")
    for person in people:
        name = person.get('name', 'N/A')
        user_id = person.get('id', 'N/A')
        login_id = person.get('login_id', 'N/A')
        enrollments = person.get('enrollments', [])
        roles = ', '.join([enr.get('role', 'N/A') for enr in enrollments])
        print(f"- {name} (User ID: {user_id}, Login ID: {login_id}, Roles: {roles})")
        # Print additional metadata if needed
        for enr in enrollments:
            print(f"    Enrollment: {enr}")

def print_assignments_by_week(token, base_url, course_id):
    """
    Print assignments grouped by week and date.
    """
    assignments = get_course_assignments(token, base_url, course_id)
    if not assignments:
        print("No assignments found or failed to fetch assignments.")
        return
    # Group assignments by ISO week
    week_groups = defaultdict(list)
    for a in assignments:
        due = a.get('due_at')
        if due:
            try:
                dt = datetime.datetime.fromisoformat(due.replace('Z', '+00:00'))
                week = dt.isocalendar().week
                year = dt.isocalendar().year
                week_groups[(year, week)].append((dt, a))
            except Exception:
                week_groups[('No Due Date', 0)].append((None, a))
        else:
            week_groups[('No Due Date', 0)].append((None, a))
    # Print assignments by week
    def week_sort_key(item):
        year, week = item[0]
        # Place 'No Due Date' (str) at the end
        if isinstance(year, int):
            return (0, year, week)
        else:
            return (1, 0, 0)
    for (year, week), items in sorted(week_groups.items(), key=week_sort_key):
        if week == 0:
            print(f"\nAssignments with No Due Date:")
        else:
            print(f"\nYear {year}, Week {week}:")
        for dt, a in sorted(items, key=lambda x: x[0] or datetime.datetime.max):
            name = a.get('name', 'Unnamed Assignment')
            due_str = dt.strftime('%Y-%m-%d %H:%M') if dt else 'No Due Date'
            print(f"  - {name} (Due: {due_str})")

def select_course_and_show_details(token, base_url, course_id):
    """
    Display details for a specific course, including name, enrollment, and dates.
    """
    details = get_course_details(token, base_url, course_id)
    if details:
        print("Course Details:")
        print(f"Name: {details.get('name', 'N/A')}")
        print(f"Enrollment Term: {details.get('enrollment_term_id', 'N/A')}")
        print(f"Start Date: {details.get('start_at', 'N/A')}")
        print(f"End Date: {details.get('end_at', 'N/A')}")
        # Optionally print all enrollments if available
        if 'enrollments' in details:
            print("Enrollments:")
            for enrollment in details['enrollments']:
                print(f"  Type: {enrollment.get('type', 'N/A')}, Role: {enrollment.get('role', 'N/A')}, State: {enrollment.get('enrollment_state', 'N/A')}")
        print_course_people(token, base_url, course_id)
        print_assignments_by_week(token, base_url, course_id)
    else:
        print("No details found for the given course ID.")

def get_canvas_courses(token, base_url):
    """
    Fetch a list of courses where the user has the "teacher" role, filtering for current semester courses.
    Args:
        token (str): Canvas API access token.
        base_url (str): Base URL of the Canvas instance.
    Returns:
        list: List of courses where the user is a teacher and that are active in the current semester.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'enrollment_state': 'active',
        'state': 'available',
        'include[]': ['enrollments', 'term'],  # Include both enrollments and term data
        'per_page': 100  # Fetch up to 100 courses per page
    }
    url = f'{base_url}/api/v1/courses'
    courses = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            batch = response.json()
            print('Batch of courses fetched:', batch)  # Debugging log
            for course in batch:
                print(f"Course ID: {course.get('id')}, Name: {course.get('name')}, Enrollments: {course.get('enrollments', [])}")
            courses.extend(batch)
            # Handle pagination
            if 'next' in response.links:
                url = response.links['next']['url']
                params = None  # Only needed for the first request
            else:
                url = None
        else:
            print(f'Failed to fetch courses. Status code: {response.status_code}')
            print(response.text)
            return []

    # Filter courses where the user has the "teacher" role
    teacher_courses = [
        course for course in courses
        if any(enrollment.get('type', '').lower() == 'teacher' for enrollment in course.get('enrollments', []))
    ]

    # Filter for current semester courses
    current_semester_courses = filter_current_semester_courses(teacher_courses)

    print('Filtered current semester teacher courses:', current_semester_courses)  # Debugging log
    return current_semester_courses


def filter_current_semester_courses(courses):
    """
    Filter courses to only include those that are active in the current semester.
    Args:
        courses (list): List of courses with term information
    Returns:
        list: Filtered list of courses active in the current semester
    """
    import datetime

    now = datetime.datetime.now()
    current_date = now.date()

    current_semester_courses = []

    for course in courses:
        term = course.get('term', {})
        if not term:
            # If no term info, include the course (fallback behavior)
            current_semester_courses.append(course)
            continue

        # Check if the course term is currently active
        start_at = term.get('start_at')
        end_at = term.get('end_at')

        # Parse term dates if available
        term_start = None
        term_end = None

        try:
            if start_at:
                term_start = datetime.datetime.fromisoformat(start_at.replace('Z', '+00:00')).date()
            if end_at:
                term_end = datetime.datetime.fromisoformat(end_at.replace('Z', '+00:00')).date()
        except ValueError:
            # If date parsing fails, include the course
            current_semester_courses.append(course)
            continue

        # Determine if course is in current semester
        is_current_semester = False

        if term_start and term_end:
            # Course has both start and end dates
            is_current_semester = term_start <= current_date <= term_end
        elif term_start and not term_end:
            # Course has start date but no end date - check if started within last 6 months
            six_months_ago = current_date - datetime.timedelta(days=180)
            is_current_semester = term_start >= six_months_ago and term_start <= current_date
        elif term_end and not term_start:
            # Course has end date but no start date - check if ends within next 6 months
            six_months_ahead = current_date + datetime.timedelta(days=180)
            is_current_semester = current_date <= term_end <= six_months_ahead
        else:
            # No term dates available, include the course
            is_current_semester = True

        # Additional check: if course is marked as published and available
        workflow_state = course.get('workflow_state', '')
        is_available = workflow_state in ['available', 'published']

        if is_current_semester and is_available:
            current_semester_courses.append(course)

    return current_semester_courses
