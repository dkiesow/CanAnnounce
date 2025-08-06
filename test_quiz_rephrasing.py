#!/usr/bin/env python3
"""
Test script to display random questions from upcoming Canvas quizzes.
Allows course selection and shows a randomly selected question from the next quiz.
"""

import sys
import os
import re
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import quiz_utils
from course_utils import get_canvas_courses
from config import canvas_token, canvas_base_url


def select_course_interactive():
    """Allow user to select a course interactively."""

    print("=" * 60)
    print("QUIZ QUESTION TEST")
    print("=" * 60)
    print()

    # Get all available courses
    print("Fetching your courses...")
    courses = get_canvas_courses(canvas_token, canvas_base_url)

    if not courses:
        print("No courses found!")
        return None

    print(f"\nFound {len(courses)} courses. Please select one:")
    print("-" * 40)

    for i, course in enumerate(courses, 1):
        course_name = course.get('name', 'Unnamed Course')
        course_id = course.get('id')
        print(f"{i}. {course_name} (ID: {course_id})")

    print("-" * 40)

    while True:
        try:
            choice = input(f"\nEnter course number (1-{len(courses)}) or 'q' to quit: ").strip()

            if choice.lower() == 'q':
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(courses):
                selected_course = courses[choice_num - 1]
                return selected_course
            else:
                print(f"Please enter a number between 1 and {len(courses)}")

        except ValueError:
            print("Please enter a valid number or 'q' to quit")


def test_quiz_question_selection():
    """Test quiz question selection for a selected course."""

    # Let user select a course
    selected_course = select_course_interactive()

    if not selected_course:
        print("No course selected. Exiting.")
        return

    course_id = selected_course.get('id')
    course_name = selected_course.get('name', 'Unnamed Course')

    print(f"\n{'='*60}")
    print(f"TESTING COURSE: {course_name}")
    print(f"Course ID: {course_id}")
    print(f"{'='*60}")

    try:
        # Get upcoming quizzes for this course
        print("\nFetching quizzes...")
        quizzes = quiz_utils.get_canvas_quizzes(course_id, canvas_token, canvas_base_url)

        if not quizzes:
            print("❌ No upcoming quizzes found in this course")
            return

        print(f"✅ Found {len(quizzes)} upcoming quiz(es)")

        # Get the next quiz (earliest due date)
        next_quiz = quizzes[0]
        quiz_title = next_quiz.get('title', 'Unnamed Quiz')
        quiz_id = next_quiz.get('id')
        due_at = next_quiz.get('due_at', 'No due date')

        print(f"\n🧪 NEXT QUIZ: {quiz_title}")
        print(f"   Due: {due_at}")
        print(f"   ID: {quiz_id}")

        # Get questions for this quiz
        questions = quiz_utils.get_quiz_questions(course_id, quiz_id, canvas_token, canvas_base_url)

        if not questions:
            print("   ❌ No questions found")
            return

        # Filter for questions with text
        text_questions = [q for q in questions if q.get('question_text')]

        if not text_questions:
            print("   ❌ No text questions found")
            return

        print(f"   📝 Found {len(text_questions)} questions.")

        # Select a random question
        selected_question = random.choice(text_questions)
        question_text = selected_question.get('question_text', '')
        question_type = selected_question.get('question_type', 'unknown')

        # Clean up HTML tags
        clean_text = re.sub(r'<[^>]+>', '', question_text).strip()

        print(f"\n   ❓ Randomly Selected Question ({question_type}):")
        print(f"   ---------------------------------------------")
        print(f"   {clean_text}")
        print(f"   ---------------------------------------------")

        # Test the main function that would be used in announcements
        print(f"\n{'='*60}")
        print("TESTING MAIN FUNCTION (get_next_quiz_question)")
        print(f"{'='*60}")

        result = quiz_utils.get_next_quiz_question(course_id)

        if result:
            print(f"✅ Function returned a question:")
            print(f"   {result}")
            print("✅ This is what would appear in announcements")
        else:
            print("❌ Function returned None")

    except Exception as e:
        print(f"❌ Error testing course: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'='*60}")
    print("Test completed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    try:
        test_quiz_question_selection()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()
