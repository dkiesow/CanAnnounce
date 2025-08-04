# Can Announce

A desktop application for creating and publishing announcements to Canvas LMS with file attachment support.

## Features

- 🎯 **Course Selection**: Choose from your Canvas courses with an intuitive interface
- 📝 **Rich Text Editor**: Create announcements with TinyMCE's powerful editor
- 📎 **File Attachments**: Upload and attach files directly to announcements
- ⏰ **Scheduling**: Schedule announcements for future publication
- ⚠️ **Smart Warnings**: Alerts when mentioning attachments without uploading files
- 📋 **Assignment Integration**: Automatically includes upcoming assignments

## Requirements

- Python 3.7+
- Canvas API token
- TinyMCE API key (free tier available)
- PyQt5 (for desktop interface)

## Installation

### Quick Install (Recommended)
```bash
git clone https://github.com/yourusername/canannounce.git
cd canannounce
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### Manual Installation
```bash
# Install system dependencies (macOS)
brew install qt@5

# Install Python dependencies
pip install -r requirements.txt
```

## Setup

1. **Copy the configuration template:**
   ```bash
   cp config_template.py config.py
   ```

2. **Get your Canvas API token:**
   - Log into Canvas → Account → Settings
   - Scroll to "Approved Integrations"
   - Click "+ New Access Token"
   - Enter purpose: "Can Announce"
   - Copy the generated token

3. **Get TinyMCE API key (free):**
   - Visit [tiny.cloud](https://www.tiny.cloud/)
   - Sign up for free account
   - Copy API key from dashboard

4. **Configure the app:**
   Edit `config.py` with your credentials:
   ```python
   CANVAS_TOKEN = 'your_canvas_api_token_here'
   CANVAS_BASE_URL = 'https://your-institution.instructure.com'
   TINYMCE_API_KEY = 'your_tinymce_api_key_here'
   ```

## Usage

### Desktop Application (Recommended)
```bash
python main.py
```

### Web Interface Only
```bash
python main_web.py
```

## Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `ANNOUNCEMENT_PUBLISH` | Publish immediately when no date selected | `False` |
| `DEFAULT_COURSE_ID` | Default course ID | `''` |
| `UPCOMING_ASSIGNMENT_DAYS` | Days ahead to fetch assignments | `60` |

## Troubleshooting

### PyQt5 Installation Issues
If you encounter "metadata-generation-failed" errors:
```bash
# Try the automated installer
./install_dependencies.sh

# Or install Qt system libraries first
brew install qt@5
pip install PyQt5
```

### Canvas API Connection Issues
- Verify your Canvas base URL (no trailing slash)
- Check that your API token hasn't expired
- Ensure your token has proper permissions

## Project Structure

```
canannounce/
├── main.py              # Desktop application entry point
├── main_web.py          # Web-only version
├── app.py               # Flask web server
├── config_template.py   # Configuration template
├── requirements.txt     # Python dependencies
├── install_dependencies.sh  # Automated installer
├── templates/           # HTML templates
├── static/             # CSS and JS files
└── utils/              # Utility modules
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security Notes

- Never commit `config.py` to version control
- Keep your Canvas API token secure
- The TinyMCE API key can be shared (it's domain-restricted)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/) and [PyQt5](https://pypi.org/project/PyQt5/)
- Rich text editing powered by [TinyMCE](https://www.tiny.cloud/)
- Canvas LMS integration via [Canvas API](https://canvas.instructure.com/doc/api/)

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Search existing [Issues](https://github.com/yourusername/canannounce/issues)
3. Create a new issue with detailed information
