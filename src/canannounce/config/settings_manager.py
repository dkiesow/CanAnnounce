"""
Settings manager for Can Announce application.
Handles loading settings from local_settings.py and user_settings.json with fallbacks.
"""
import json
import os
from typing import Dict, Any

class SettingsManager:
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.dirname(__file__)
        self.config_dir = config_dir
        self.user_settings_file = os.path.join(config_dir, 'user_settings.json')
        self._default_settings = {}
        self._user_settings = {}
        self.load_settings()

    def load_settings(self):
        """Load settings from local_settings.py and user_settings.json"""
        # Load default settings from local_settings.py
        try:
            from . import local_settings
            if hasattr(local_settings, 'CONFIG_SETTINGS'):
                self._default_settings = local_settings.CONFIG_SETTINGS
            else:
                # Fallback for legacy format
                self._create_legacy_config_settings(local_settings)
        except ImportError:
            print("Warning: local_settings.py not found, using minimal defaults")
            local_settings = None
            self._create_minimal_defaults()

        # Load user settings from JSON file
        self._load_user_settings()

    def _create_legacy_config_settings(self, local_settings):
        """Create CONFIG_SETTINGS from legacy individual variables"""
        legacy_vars = {
            'ANNOUNCEMENT_NOW': getattr(local_settings, 'ANNOUNCEMENT_NOW', False),
            'canvas_token': getattr(local_settings, 'canvas_token', ''),
            'canvas_base_url': getattr(local_settings, 'canvas_base_url', ''),
            'DEFAULT_COURSE_ID': getattr(local_settings, 'DEFAULT_COURSE_ID', ''),
            'UPCOMING_ASSIGNMENT_DAYS': getattr(local_settings, 'UPCOMING_ASSIGNMENT_DAYS', 30),
            'TINYMCE_API_KEY': getattr(local_settings, 'TINYMCE_API_KEY', ''),
            'INCLUDE_QUIZ_QUESTION': getattr(local_settings, 'INCLUDE_QUIZ_QUESTION', True),
            'QUIZ_QUESTION_PROMPT': getattr(local_settings, 'QUIZ_QUESTION_PROMPT', 'Practice Question from Upcoming Quiz'),
        }

        self._default_settings = {}
        for key, value in legacy_vars.items():
            setting_type = 'boolean' if isinstance(value, bool) else 'integer' if isinstance(value, int) else 'string'
            sensitive = key in ['canvas_token', 'TINYMCE_API_KEY']
            self._default_settings[key] = {
                'value': value,
                'label': key.replace('_', ' ').title(),
                'description': f'Configuration for {key}',
                'type': setting_type,
                'sensitive': sensitive
            }

    def _create_minimal_defaults(self):
        """Create minimal default settings if no local_settings.py exists"""
        self._default_settings = {
            'ANNOUNCEMENT_NOW': {
                'value': False,
                'label': 'Publish Immediately',
                'description': 'Set to True to publish announcements immediately',
                'type': 'boolean'
            },
            'canvas_token': {
                'value': '',
                'label': 'Canvas API Token',
                'description': 'Canvas API token for authentication',
                'type': 'string',
                'sensitive': True
            },
            'canvas_base_url': {
                'value': '',
                'label': 'Canvas Base URL',
                'description': 'Canvas base URL for your institution',
                'type': 'string'
            }
        }

    def _load_user_settings(self):
        """Load user settings from JSON file"""
        try:
            if os.path.exists(self.user_settings_file):
                with open(self.user_settings_file, 'r') as f:
                    self._user_settings = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load user settings: {e}")
            self._user_settings = {}

    def save_user_settings(self, settings: Dict[str, Any]) -> bool:
        """Save user settings to JSON file"""
        try:
            # Only save non-sensitive settings to user_settings.json
            filtered_settings = {}
            for key, value in settings.items():
                if key in self._default_settings:
                    if not self._default_settings[key].get('sensitive', False):
                        filtered_settings[key] = value

            with open(self.user_settings_file, 'w') as f:
                json.dump(filtered_settings, f, indent=2)

            # Update in-memory user settings
            self._user_settings = filtered_settings
            return True
        except IOError as e:
            print(f"Error saving user settings: {e}")
            return False

    def get_setting(self, key: str, default=None):
        """Get a setting value with user override, fallback to default"""
        # Check user settings first (non-sensitive only)
        if key in self._user_settings:
            return self._user_settings[key]

        # Fallback to default settings
        if key in self._default_settings:
            return self._default_settings[key]['value']

        return default

    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get all settings with metadata for UI display"""
        result = {}
        for key, config in self._default_settings.items():
            result[key] = {
                'value': self.get_setting(key, config['value']),
                'label': config['label'],
                'description': config['description'],
                'type': config['type'],
                'sensitive': config.get('sensitive', False),
                'user_overridden': key in self._user_settings
            }
        return result

    def get_non_sensitive_settings(self) -> Dict[str, Any]:
        """Get only non-sensitive settings for user editing"""
        result = {}
        for key, config in self._default_settings.items():
            if not config.get('sensitive', False):
                result[key] = {
                    'value': self.get_setting(key, config['value']),
                    'label': config['label'],
                    'description': config['description'],
                    'type': config['type']
                }
        return result

# Global settings manager instance
settings_manager = SettingsManager()
