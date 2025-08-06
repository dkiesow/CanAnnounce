# local_settings_template.py
# Copy this file to local_settings.py and update with your specific values
# DO NOT commit your actual local_settings.py file to version control

# Configuration with labels for Flask UI
CONFIG_SETTINGS = {
    'ANNOUNCEMENT_NOW': {
        'value': False,
        'label': 'Publish Immediately',
        'description': 'Set to True to publish announcements immediately, False to schedule 30 days in the future',
        'type': 'boolean'
    },
    'canvas_token': {
        'value': 'YOUR_CANVAS_API_TOKEN_HERE',
        'label': 'Canvas API Token',
        'description': 'Get your token from Canvas -> Account -> Settings -> New Access Token',
        'type': 'string',
        'sensitive': True
    },
    'canvas_base_url': {
        'value': 'https://yourschool.instructure.com',
        'label': 'Canvas Base URL',
        'description': 'Canvas base URL for your institution (e.g., https://canvas.instructure.com)',
        'type': 'string'
    },
    'DEFAULT_COURSE_ID': {
        'value': 'YOUR_DEFAULT_COURSE_ID',
        'label': 'Default Course ID',
        'description': 'Default course ID if none is provided',
        'type': 'string'
    },
    'UPCOMING_ASSIGNMENT_DAYS': {
        'value': 30,
        'label': 'Upcoming Assignment Days',
        'description': 'Number of days to look ahead for upcoming assignments in announcements',
        'type': 'integer'
    },
    'TINYMCE_API_KEY': {
        'value': 'YOUR_TINYMCE_API_KEY_HERE',
        'label': 'TinyMCE API Key',
        'description': 'Get a free API key from https://www.tiny.cloud/',
        'type': 'string',
        'sensitive': True
    },
    'INCLUDE_QUIZ_QUESTION': {
        'value': True,
        'label': 'Include Quiz Question',
        'description': 'Set to False to disable quiz questions',
        'type': 'boolean'
    },
    'QUIZ_QUESTION_PROMPT': {
        'value': 'Practice Question from Upcoming Quiz',
        'label': 'Quiz Question Prompt',
        'description': 'Text to display before quiz questions',
        'type': 'string'
    }
}

# Legacy individual variables for backward compatibility
ANNOUNCEMENT_NOW = CONFIG_SETTINGS['ANNOUNCEMENT_NOW']['value']
canvas_token = CONFIG_SETTINGS['canvas_token']['value']
canvas_base_url = CONFIG_SETTINGS['canvas_base_url']['value']
DEFAULT_COURSE_ID = CONFIG_SETTINGS['DEFAULT_COURSE_ID']['value']
UPCOMING_ASSIGNMENT_DAYS = CONFIG_SETTINGS['UPCOMING_ASSIGNMENT_DAYS']['value']
TINYMCE_API_KEY = CONFIG_SETTINGS['TINYMCE_API_KEY']['value']
INCLUDE_QUIZ_QUESTION = CONFIG_SETTINGS['INCLUDE_QUIZ_QUESTION']['value']
QUIZ_QUESTION_PROMPT = CONFIG_SETTINGS['QUIZ_QUESTION_PROMPT']['value']
