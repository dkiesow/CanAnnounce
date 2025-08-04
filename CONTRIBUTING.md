# Contributing to Canvas Announcer

Thank you for considering contributing to Canvas Announcer! This document provides guidelines for contributing to the project.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include screenshots if possible**
- **Include your environment details**:
  - OS version (macOS, Windows, Linux)
  - Python version
  - PyQt5 version
  - Canvas instance type

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the enhancement**
- **Describe the current behavior and explain the behavior you expected**
- **Explain why this enhancement would be useful**

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test your changes thoroughly**
5. **Commit your changes** with descriptive messages:
   ```bash
   git commit -m "Add feature: descriptive message"
   ```
6. **Push to your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**

## Development Setup

1. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/canannounce.git
   cd canannounce
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   ./install_dependencies.sh
   # OR manually:
   pip install -r requirements.txt
   ```

4. **Set up configuration**:
   ```bash
   cp config_template.py config.py
   # Edit config.py with your test credentials
   ```

## Coding Standards

### Python Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small

### File Organization
- Keep related functionality in appropriate modules
- Use relative imports within the project
- Maintain consistent file structure

### Testing
- Test your changes thoroughly before submitting
- Include both positive and negative test cases
- Test with different Canvas instances if possible

## Project Structure

```
canannounce/
├── main.py                 # Desktop app entry point
├── main_web.py            # Web-only entry point
├── app.py                 # Flask application
├── config_template.py     # Configuration template
├── announcement_utils.py  # Announcement utilities
├── course_utils.py        # Course management utilities
├── templates/             # HTML templates
│   ├── modal.html
│   └── select_course.html
├── static/                # Static assets
│   └── styles.css
└── utils/                 # Additional utilities
```

## Commit Message Guidelines

Use clear and meaningful commit messages:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that don't affect code meaning (formatting, etc.)
- **refactor**: Code changes that neither fix bugs nor add features
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to build process or auxiliary tools

Examples:
```
feat: add support for announcement templates
fix: resolve PyQt5 installation issues on Apple Silicon
docs: update README with troubleshooting section
```

## Security Considerations

- **Never commit sensitive data** (API tokens, passwords)
- **Use config_template.py** for example configurations
- **Validate all user inputs** in form handlers
- **Follow Canvas API best practices**

## Questions?

If you have questions about contributing, please:
1. Check existing issues and discussions
2. Create a new issue with the "question" label
3. Be specific about what you need help with

Thank you for contributing to Canvas Announcer!
