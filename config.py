# config.py
# Configuration for announcement posting

# Set to True to publish announcements immediately, False to schedule 30 days in the future
ANNOUNCEMENT_NOW = False

# Canvas API token for authentication
canvas_token = '***REMOVED***'

# Canvas base URL for your institution
canvas_base_url = 'https://umsystem.instructure.com'  # e.g., https://canvas.instructure.com or your institution's Canvas URL

# Default course ID if none is provided
DEFAULT_COURSE_ID = '335050'

# Number of days to look ahead for upcoming assignments in announcements
UPCOMING_ASSIGNMENT_DAYS = 60

# TinyMCE API key for rich text editor
TINYMCE_API_KEY = '***REMOVED***'

# Quiz question configuration
INCLUDE_QUIZ_QUESTION = True  # Set to True to include quiz questions in announcements
QUIZ_QUESTION_PROMPT = "On the Quiz, expect to be asked about"  # Configurable prompt text
