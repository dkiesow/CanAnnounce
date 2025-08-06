import random
import requests
from datetime import datetime, timezone, timedelta
from config import canvas_token, canvas_base_url


def get_canvas_quizzes(course_id, token, base_url):
    """
    Fetch upcoming quizzes for a specific course from Canvas API.

    Args:
        course_id (str): Canvas course ID
        token (str): Canvas API access token
        base_url (str): Canvas base URL

    Returns:
        list: List of upcoming quizzes sorted by due date
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f"{base_url}/api/v1/courses/{course_id}/quizzes"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            quizzes = response.json()

            # Filter for upcoming quizzes with due dates
            now = datetime.now(timezone.utc)
            upcoming_quizzes = []

            for quiz in quizzes:
                if quiz.get('due_at'):
                    due_date = datetime.fromisoformat(quiz['due_at'].replace('Z', '+00:00'))
                    if due_date > now:
                        upcoming_quizzes.append(quiz)

            # Sort by due date (earliest first)
            upcoming_quizzes.sort(key=lambda x: x['due_at'])
            return upcoming_quizzes
        else:
            print(f"Failed to fetch quizzes. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching quizzes: {e}")
        return []


def get_quiz_questions(course_id, quiz_id, token, base_url):
    """
    Fetch questions for a specific quiz from Canvas API.

    Args:
        course_id (str): Canvas course ID
        quiz_id (str): Canvas quiz ID
        token (str): Canvas API access token
        base_url (str): Canvas base URL

    Returns:
        list: List of quiz questions
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f"{base_url}/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch quiz questions. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching quiz questions: {e}")
        return []


def get_next_quiz_question(course_id=None):
    """
    Fetch a random question from the next quiz in a course.

    Args:
        course_id (str, optional): Canvas course ID. If not provided, tries to get from request context

    Returns:
        str: Full text of a randomly selected quiz question or None if no questions found
    """
    if not course_id:
        # Try to get course_id from Flask request context
        try:
            from flask import request
            course_id = request.form.get('course_id') or request.args.get('course_id')
        except:
            # If no Flask context, return None
            course_id = None

    if not course_id:
        print("No course ID provided")
        return None

    try:
        # Get upcoming quizzes
        quizzes = get_canvas_quizzes(course_id, canvas_token, canvas_base_url)

        # If no quizzes exist, return None immediately
        if not quizzes:
            print(f"No upcoming quizzes found for course {course_id}")
            return None

        # Get the next quiz (earliest due date)
        next_quiz = quizzes[0]
        print(f"Found next quiz: {next_quiz.get('title', 'Unnamed Quiz')} (ID: {next_quiz.get('id')})")

        # Get questions for the next quiz
        questions = get_quiz_questions(course_id, next_quiz['id'], canvas_token, canvas_base_url)

        if not questions:
            print(f"No questions found for quiz {next_quiz.get('id')}")
            return None

        # Filter for questions with text
        text_questions = [q for q in questions if q.get('question_text')]

        if not text_questions:
            print(f"No valid question text found in quiz {next_quiz.get('id')}")
            return None

        # Simply select a random question
        selected_question = random.choice(text_questions)
        question_text = selected_question.get('question_text', '')

        # Clean up HTML tags if present
        import re
        question_text = re.sub(r'<[^>]+>', '', question_text)
        question_text = question_text.strip()

        # Validate the question has some content
        if question_text and len(question_text) > 10:
            print(f"Selected random quiz question: {question_text[:50]}...")
            return question_text
        else:
            print(f"Selected question was too short or empty")
            return None

    except Exception as e:
        print(f"Error getting quiz question: {e}")
        return None
