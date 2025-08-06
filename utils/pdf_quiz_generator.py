"""
PDF-based quiz content extractor.
Extracts potential quiz questions from uploaded PDFs.
"""

import PyPDF2
import re
import random
from io import BytesIO


def extract_text_from_pdf(file_path_or_bytes):
    """
    Extract text from a PDF file.

    Args:
        file_path_or_bytes: Either a file path string or bytes object

    Returns:
        str: Extracted text from the PDF
    """
    try:
        if isinstance(file_path_or_bytes, str):
            with open(file_path_or_bytes, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        else:
            # Handle bytes object (from file upload)
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_path_or_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

        return clean_extracted_text(text)
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""


def clean_extracted_text(text):
    """
    Clean and normalize extracted PDF text.

    Args:
        text (str): Raw extracted text

    Returns:
        str: Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove page numbers and common PDF artifacts
    text = re.sub(r'\d+/\d+', '', text)  # Page numbers like 1/10
    text = re.sub(r'Page \d+', '', text)

    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def extract_potential_questions_from_pdf(text):
    """
    Extract content that looks like potential quiz questions from PDF text.

    Args:
        text (str): Cleaned text from PDF

    Returns:
        list: List of potential questions found in the PDF
    """
    if not text or len(text.strip()) < 100:
        return []

    questions = []

    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Look for question-like sentences
    for sentence in sentences:
        sentence = sentence.strip()
        # Check if it's a reasonable length for a question
        if 20 <= len(sentence) <= 300:
            # Check if it starts with a question word or has a question mark
            if (re.match(r'^(What|Why|How|Which|When|Where|Who|Describe|Explain|Define|Identify|Compare)', sentence, re.IGNORECASE)
                or '?' in sentence):
                questions.append(sentence)

    # Also look for numbered or bullet-pointed items that might be questions
    list_items = re.findall(r'(?:^|\n)(?:\d+[.)]|\*|\-)\s+([A-Z][^.!?\n]+[.!?])', text, re.MULTILINE)
    for item in list_items:
        if 20 <= len(item) <= 300 and item.strip() not in questions:
            questions.append(item.strip())

    # Look for "question:" patterns
    question_patterns = re.findall(r'(?:question|quiz|problem|exercise)[:\-]?\s+([A-Z][^.!?\n]+[.!?])', text, re.IGNORECASE | re.MULTILINE)
    for q in question_patterns:
        if 20 <= len(q) <= 300 and q.strip() not in questions:
            questions.append(q.strip())

    return questions


def generate_quiz_question_from_pdf(file_path_or_bytes):
    """
    Extract a potential quiz question from PDF content.

    Args:
        file_path_or_bytes: PDF file path or bytes

    Returns:
        str: A randomly selected potential quiz question or None if failed
    """
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file_path_or_bytes)

        if not text or len(text.strip()) < 100:
            return None

        # Extract potential questions from the text
        questions = extract_potential_questions_from_pdf(text)

        if questions:
            # Select a random question
            selected_question = random.choice(questions)

            # Ensure proper punctuation
            if not selected_question.endswith(('.', '!', '?')):
                if '?' in selected_question:
                    selected_question += '?'
                else:
                    selected_question += '.'

            print(f"PDF QUESTION EXTRACTED: {selected_question[:50]}...")
            return selected_question
        else:
            # If no clear questions are found, extract a random interesting sentence
            sentences = re.split(r'(?<=[.!?])\s+', text)
            content_sentences = [s for s in sentences if 50 <= len(s) <= 300 and re.search(r'\b(concept|theory|principle|idea|process|method|system)\b', s, re.IGNORECASE)]

            if content_sentences:
                selected_sentence = random.choice(content_sentences)
                print(f"PDF CONTENT EXTRACTED: {selected_sentence[:50]}...")
                return selected_sentence

            return None

    except Exception as e:
        print(f"Error generating question from PDF: {e}")
        return None
