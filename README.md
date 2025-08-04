# Can Announce

A desktop application for creating and publishing announcements to Canvas LMS with file attachment support.

## Platform Support

Can Announce may run on multiple operating systems:
- **macOS** (Primary development platform)
- **Windows** (With Windows-specific installation script)
- **Ubuntu/Linux** (Tested via CI/CD)

Non-Mac platforms are not all at effectively tested either for installation or operation. But should work in theory.
## Requirements

- Python 3.7+
- Canvas API token
- TinyMCE API key (free tier available)
- PyQt5 (for desktop interface)

## Installation

### macOS (Recommended)
```bash
git clone https://github.com/yourusername/canannounce.git
cd canannounce
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### Windows
```cmd
git clone https://github.com/yourusername/canannounce.git
cd canannounce
install_dependencies.bat
```

### Ubuntu/Linux
```bash
git clone https://github.com/yourusername/canannounce.git
cd canannounce
sudo apt update
sudo apt install python3-pip python3-venv qt5-default
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### Manual Installation (All Platforms)
```bash
# Install system dependencies (platform-specific)
# macOS: brew install qt@5
# Ubuntu: sudo apt install qt5-default
# Windows: Dependencies handled by pip

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
# All platforms
python main.py
```

### Web Interface Only
```bash
# All platforms
python main_web.py
```

## Platform-Specific Notes

### Windows Users
- Use `install_dependencies.bat` instead of the shell script
- Some antivirus software may flag the executable - this is normal for PyQt5 applications
- If PyQt5 installation fails, install Visual Studio Build Tools

### Linux Users
- Install Qt5 development packages: `sudo apt install qt5-default libqt5gui5-dev`
- Use `python3` instead of `python` on most distributions
- Some distributions may require `python3-pip` package

### macOS Users
- Install Homebrew Qt5 for best compatibility: `brew install qt@5`
- Apple Silicon (M1/M2) users may need Rosetta for some PyQt5 dependencies

## Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `ANNOUNCEMENT_PUBLISH` | Publish immediately when no date selected | `False` |
| `DEFAULT_COURSE_ID` | Default course ID | `''` |
| `UPCOMING_ASSIGNMENT_DAYS` | Days ahead to fetch assignments | `60` |

## Troubleshooting

### PyQt5 Installation Issues
**All Platforms:**
```bash
# Try the automated installer first
./install_dependencies.sh  # macOS/Linux
install_dependencies.bat   # Windows
```

**Platform-specific solutions:**

**macOS:**
```bash
brew install qt@5
export PATH="/opt/homebrew/opt/qt@5/bin:$PATH"  # Apple Silicon
# or export PATH="/usr/local/opt/qt@5/bin:$PATH"  # Intel
pip install PyQt5
```

**Windows:**
```cmd
# Install Visual Studio Build Tools if needed
pip install --only-binary=all PyQt5
```

**Ubuntu/Linux:**
```bash
sudo apt install qt5-default libqt5gui5-dev
pip install PyQt5
```

### Canvas API Connection Issues
- Verify your Canvas base URL (no trailing slash)
- Check that your API token hasn't expired
- Ensure your token has proper permissions

## Project Structure

```
canannounce/
├── main.py                    # Desktop application entry point
├── main_web.py               # Web-only version
├── app.py                    # Flask web server
├── config_template.py        # Configuration template
├── requirements.txt          # Python dependencies
├── install_dependencies.sh   # Unix/Linux installer
├── install_dependencies.bat  # Windows installer
├── templates/                # HTML templates
├── static/                   # CSS and JS files
└── utils/                    # Utility modules
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Continuous Integration

This project is tested on multiple platforms using GitHub Actions:
- **Ubuntu Latest** - Python 3.8, 3.9, 3.10, 3.11
- **macOS Latest** - Python 3.8, 3.9, 3.10, 3.11  
- **Windows Latest** - Python 3.8, 3.9, 3.10, 3.11

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

For platform-specific issues, please include:
- Operating system and version
- Python version (`python --version`)
- Error messages or logs
