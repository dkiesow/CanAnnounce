"""
Quiz utilities for extracting questions from Canvas quizzes.
"""
import random
import requests
from datetime import datetime, timezone

from canannounce.config import canvas_token, canvas_base_url


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


def get_next_quiz_question(course_id):
    """
    Get a random question from upcoming quizzes in the course.

    Args:
        course_id (str): Canvas course ID

    Returns:
        str: A random quiz question, or None if no questions found
    """
    try:
        quizzes = get_canvas_quizzes(course_id, canvas_token, canvas_base_url)
        if not quizzes:
            return None

        # Get questions from all upcoming quizzes
        all_questions = []
        for quiz in quizzes:
            questions = get_quiz_questions(course_id, quiz['id'], canvas_token, canvas_base_url)
            if questions:
                # Filter for questions with text content
                text_questions = [q for q in questions if q.get('question_text')]
                all_questions.extend(text_questions)

        if all_questions:
            # Select a random question
            selected_question = random.choice(all_questions)
            question_text = selected_question.get('question_text', '')

            # Clean up HTML tags if present
            import re
            question_text = re.sub(r'<[^>]+>', '', question_text)
            question_text = question_text.strip()

            # Return the question if it has meaningful content
            if question_text and len(question_text) > 10:
                return question_text

        return None

    except Exception as e:
        print(f"Error getting quiz question: {e}")
        return None
