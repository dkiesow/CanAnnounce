# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### Do NOT create a public issue

Security vulnerabilities should not be reported through public GitHub issues.

### How to Report

1. **Email**: Send details to [your-email@example.com]
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Your contact information

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Response**: Within 1 week
- **Resolution Timeline**: Varies based on severity

### Security Considerations

This application handles:
- **Canvas API Tokens**: Stored in local config files
- **File Uploads**: Temporary files processed locally
- **Network Requests**: To Canvas LMS and TinyMCE APIs

### Best Practices for Users

- Keep your Canvas API token secure
- Don't commit `config.py` to version control
- Use the latest version of the application
- Run the application in a secure environment

### Disclosure Policy

- We will coordinate with you on disclosure timing
- Credit will be given for responsible disclosure
- We aim to fix critical issues within 30 days
