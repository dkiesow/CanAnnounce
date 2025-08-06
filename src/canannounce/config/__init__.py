"""
Configuration settings for the canannounce application.
"""
import os
from pathlib import Path

# Canvas API settings
canvas_token = os.environ.get('CANVAS_API_TOKEN', '')
canvas_base_url = os.environ.get('CANVAS_BASE_URL', 'https://canvas.instructure.com')

# TinyMCE API key for rich text editor
TINYMCE_API_KEY = os.environ.get('TINYMCE_API_KEY', '')

# Announcement settings
ANNOUNCEMENT_NOW = os.environ.get('ANNOUNCEMENT_NOW', 'true').lower() in ('true', 'yes', '1')

# Quiz question settings
INCLUDE_QUIZ_QUESTION = os.environ.get('INCLUDE_QUIZ_QUESTION', 'false').lower() in ('true', 'yes', '1')
QUIZ_QUESTION_PROMPT = os.environ.get('QUIZ_QUESTION_PROMPT', 'Practice Question from Upcoming Quiz')

# Application paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
STATIC_DIR = BASE_DIR / 'static'
TEMPLATES_DIR = BASE_DIR / 'templates'
UPLOADS_DIR = BASE_DIR / 'uploads'

# Create uploads directory if it doesn't exist
UPLOADS_DIR.mkdir(exist_ok=True)

# Load local settings if available
try:
    from .local_settings import *
except ImportError:
    pass
