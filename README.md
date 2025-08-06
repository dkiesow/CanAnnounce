# CanAnnounce

A tool for creating and managing Canvas announcements with file attachments and quiz question integration.

## Features

- Create Canvas announcements with file attachments
- Automatically include information about upcoming assignments  
- Option to include a random question from upcoming quizzes
- Web interface for easy announcement creation
- Command-line interface for scripting and automation
- Easy configuration management
- Timezone-aware date handling

## Quick Start

This was developed and tested ONLY on a Mac. It may work on other platforms, but it is not tested or guaranteed.

### Method 1: One-Click Install (Recommended)

**Linux/macOS:**
```bash
git clone https://github.com/yourusername/canannounce.git
cd canannounce
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
git clone https://github.com/yourusername/canannounce.git
cd canannounce
install.bat
```

### Method 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/canannounce.git
cd canannounce

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate.bat  # Windows

# Install
pip install -e .
```

### Method 3: Install from PyPI (when available)

**Web Interface Only (Default):**
```bash
pip install canannounce
```

**With Optional GUI Support:**
```bash
pip install canannounce[gui]
```

**All Features (GUI + Development Tools):**
```bash
pip install canannounce[gui,dev]
```

## Configuration

After installation, run the configuration wizard:

```bash
canannounce-setup
```

This will create a configuration file in your user directory:
- **Linux:** `~/.config/canannounce/local_settings.py`
- **macOS:** `~/Library/Application Support/canannounce/local_settings.py`  
- **Windows:** `%APPDATA%\Local\canannounce\local_settings.py`

### Required Configuration

You'll need:
1. **Canvas Base URL** (e.g., `https://your-school.instructure.com`)
2. **Canvas API Token** (generate from Canvas Account → Settings → New Access Token)
3. **TinyMCE API Key** (optional, for rich text editing - get free key from tiny.cloud)

## Usage

### Web Interface (Recommended)

```bash
canannounce
```

Then open your browser to `http://localhost:5000`

### Command Line

```bash
canannounce-web  # Alternative web interface command
```

## File Structure

```
~/.config/canannounce/           # User config directory
├── local_settings.py            # Main configuration  
├── user_settings.json          # UI preferences (auto-generated)
└── README.txt                  # Quick reference
```

## Configuration Options

Edit your `local_settings.py` file:

```python
# Canvas Configuration
canvas_base_url = "https://your-school.instructure.com"
canvas_token = "your_api_token_here"

# TinyMCE Configuration (optional)
TINYMCE_API_KEY = "your_tinymce_key"

# Assignment Settings
UPCOMING_ASSIGNMENT_DAYS = 30

# Quiz Settings  
INCLUDE_QUIZ_QUESTION = True
QUIZ_QUESTION_PROMPT = "Practice Question"

# Announcement Settings
ANNOUNCEMENT_NOW = False
```

## Development

### Building from Source

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Build distribution packages
chmod +x build_dist.sh
./build_dist.sh
```

### Project Structure

```
src/canannounce/
├── config/              # Configuration management
├── core/               # Core Canvas API utilities  
├── utils/              # Helper utilities
└── web/                # Web interface
    ├── templates/      # HTML templates
    └── static/         # CSS/JS assets
```

## Troubleshooting

### Configuration Issues

If you get configuration errors:
```bash
canannounce-setup  # Re-run setup wizard
```

### Permission Issues

Make sure your Canvas API token has the required permissions:
- Read course content
- Create announcements
- Upload files

### Timezone Issues

The app automatically converts Canvas UTC timestamps to your local timezone. If dates appear incorrect, check your system timezone settings.

## Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/canannounce/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/canannounce/discussions)
- **Config Location:** Run `canannounce-setup` to see your config directory

## License

MIT License - see LICENSE file for details.
