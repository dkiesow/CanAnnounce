# config_template.py
# Configuration template for Can Announce
#
# INSTRUCTIONS:
# 1. Copy this file to 'config.py' in the same directory
# 2. Replace all dummy values with your actual credentials and settings
# 3. Never commit the actual config.py file to version control

# ==============================================================================
# CANVAS API CONFIGURATION
# ==============================================================================

# Your Canvas API access token
# To get this token:
# 1. Log into your Canvas instance
# 2. Go to Account → Settings
# 3. Scroll down to "Approved Integrations"
# 4. Click "+ New Access Token"
# 5. Enter a purpose (e.g., "Can Announce App")
# 6. Set expiration date (optional)
# 7. Click "Generate Token" and copy the token
CANVAS_TOKEN = 'your_canvas_api_token_here_1234567890abcdefghijklmnopqrstuvwxyz'

# Your institution's Canvas base URL
# Examples:
#   - https://canvas.instructure.com (for Canvas Cloud)
#   - https://youruniversity.instructure.com
#   - https://canvas.yourschool.edu
# DO NOT include trailing slash
CANVAS_BASE_URL = 'https://your-institution.instructure.com'

# ==============================================================================
# COURSE CONFIGURATION
# ==============================================================================

# Default course ID to use if none is provided
# You can find this in the URL when viewing a course:
# https://your-canvas.com/courses/123456 (the number is the course ID)
# This is optional - leave as empty string if not needed
DEFAULT_COURSE_ID = '123456'

# Number of days to look ahead for upcoming assignments
# These assignments will be automatically included in announcement templates
UPCOMING_ASSIGNMENT_DAYS = 5

# ==============================================================================
# TINYMCE EDITOR CONFIGURATION
# ==============================================================================

# TinyMCE API key for the rich text editor
# To get this key:
# 1. Go to https://www.tiny.cloud/
# 2. Sign up for a free account
# 3. Go to the Dashboard
# 4. Copy your API key from the "API Key" section
# The free tier allows up to 1,000 loads per month
TINYMCE_API_KEY = 'your_tinymce_api_key_here_abcdefghijklmnopqrstuvwxyz123456'

# ==============================================================================
# ANNOUNCEMENT PUBLISHING CONFIGURATION
# ==============================================================================

# Controls what happens when no publish date is selected in the datepicker
# Set to True: Publish announcements immediately when no date is selected
# Set to False: Schedule announcements 30 days in the future when no date is selected
#
# NOTE: This setting does NOT disable the datepicker. Users can always override
# this behavior by selecting a specific date/time in the datepicker interface.
# This only affects the fallback behavior when the datepicker is left empty.
ANNOUNCEMENT_NOW = False

# ==============================================================================
# ADDITIONAL NOTES
# ==============================================================================
#
# Security Notes:
# - Keep your Canvas token secure and never share it
# - Canvas tokens can be revoked from your Canvas account settings
# - Consider setting an expiration date on your Canvas token
#
# Troubleshooting:
# - If Canvas API calls fail, verify your token and base URL
# - If TinyMCE doesn't load, check your API key and internet connection
# - Check Canvas API documentation for rate limits and permissions
#
