# local_settings_template.py
# Copy this file to local_settings.py and update with your specific values
# DO NOT commit your actual local_settings.py file to version control

# Set to True to publish announcements immediately, False to schedule 30 days in the future
ANNOUNCEMENT_NOW = False

# Canvas API token for authentication
# Get your token from Canvas -> Account -> Settings -> New Access Token
canvas_token = 'YOUR_CANVAS_API_TOKEN_HERE'

# Canvas base URL for your institution
canvas_base_url = 'https://yourschool.instructure.com'  # e.g., https://canvas.instructure.com or your institution's Canvas URL

# Default course ID if none is provided
DEFAULT_COURSE_ID = 'YOUR_DEFAULT_COURSE_ID'

# Number of days to look ahead for upcoming assignments in announcements
UPCOMING_ASSIGNMENT_DAYS = 30

# TinyMCE API key for rich text editor
# Get a free API key from https://www.tiny.cloud/
TINYMCE_API_KEY = 'YOUR_TINYMCE_API_KEY_HERE'

# Quiz question settings
INCLUDE_QUIZ_QUESTION = True  # Set to False to disable quiz questions
QUIZ_QUESTION_PROMPT = 'Practice Question from Upcoming Quiz'
