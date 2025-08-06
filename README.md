# CanAnnounce

A tool for creating and managing Canvas announcements with file attachments and quiz question integration.

## Features

- Create Canvas announcements with file attachments
- Automatically include information about upcoming assignments
- Option to include a random question from upcoming quizzes
- Web interface for easy announcement creation
- Command-line interface for scripting and automation

## Installation

### Option 1: Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/canannounce.git
cd canannounce

# Install the package and dependencies
pip install -e .
```

### Option 2: Quick start with the run script

```bash
# Clone the repository
git clone https://github.com/yourusername/canannounce.git
cd canannounce

# Install dependencies
pip install -r requirements.txt

# Run the web application
python run.py
```

## Configuration

Create a `config.py` file based on the provided `config_template.py` or set environment variables:

```python
# Canvas API settings
canvas_token = 'your_canvas_api_token'
canvas_base_url = 'https://your-institution.instructure.com'

# TinyMCE API key for rich text editor
TINYMCE_API_KEY = 'your_tinymce_api_key'

# Announcement settings
ANNOUNCEMENT_NOW = True  # Set to False to use the scheduled time

# Quiz question settings
INCLUDE_QUIZ_QUESTION = True  # Set to False to disable quiz questions
QUIZ_QUESTION_PROMPT = 'Practice Question from Upcoming Quiz'
```

## Usage

### Web Interface

Start the web server:

```bash
# Using the package
canannounce-web

# Or using the run script
python run.py
```

Then open your browser to http://localhost:5000

### Command Line

List available courses:

```bash
canannounce --list-courses
```

Upload a file and create an announcement:

```bash
canannounce --course-id 12345 --title "Today's Lecture" --body "<p>Here are today's slides</p>" --file path/to/slides.pdf
```

## Project Structure

The project follows a standard Python package structure:

- `src/canannounce/`: Main package directory
  - `api/`: API-related functionality
  - `config/`: Configuration settings
  - `core/`: Core functionality like course utilities
  - `utils/`: Helper functions for quizzes and announcements
  - `web/`: Flask web application code
- `static/`: Static assets for the web interface
- `templates/`: HTML templates for the web interface

## Development

1. Fork and clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
4. Install dev dependencies: `pip install -e ".[dev]"`
5. Run tests: `pytest`

## License

[MIT License](LICENSE)
