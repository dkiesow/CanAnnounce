# CanAnnounce Release Notes

## Version 1.6.0 - August 6, 2025

### 🎯 Major Improvements

#### Assignment Date Display Fixes
- **Fixed timezone conversion issues** - Assignment due dates now correctly display in local time instead of UTC
- **Added day of week** - Due dates now show as "Fri Sep 19" instead of just "Sep 19"
- **Removed year from dates** - Cleaner display without redundant year information
- **Fixed date rounding** - Assignments due at 11:59 PM no longer incorrectly round up to the next day

#### Complete Packaging & Distribution Solution
- **Enhanced setup.py** with proper metadata, dependencies, and console scripts
- **Added PyQt6 support** as optional dependency (`pip install canannounce[gui]`)
- **Cross-platform installation scripts** - One-click install for Linux/macOS and Windows
- **Interactive configuration wizard** - `canannounce-setup` command for easy initial setup
- **Platform-specific config directories** - Settings now stored in standard user directories:
  - macOS: `~/Library/Application Support/canannounce/`
  - Linux: `~/.config/canannounce/`
  - Windows: `%APPDATA%\Local\canannounce/`

#### Project Organization
- **Reorganized script structure** - All installation and build scripts moved to `scripts/` directory
- **Fixed script path issues** - Scripts now work correctly from their new locations
- **Cleaner root directory** - Better separation of core files and utility scripts
- **Updated documentation** - README reflects new installation methods and file locations

### 🔧 Technical Improvements

#### Configuration Management
- **User config isolation** - User settings separate from package code for easier updates
- **Fallback system** - Graceful handling when config files are missing
- **Settings validation** - Better error messages for configuration issues

#### Development Experience
- **Distribution tools** - `build_dist.sh` script for creating PyPI packages
- **Package manifest** - Proper file inclusion with MANIFEST.in
- **Development dependencies** - Optional dev tools via `pip install canannounce[dev]`

#### User Interface
- **Fixed HTML entities** - Alert dialogs no longer show `&quot;` artifacts
- **Improved error handling** - Better user feedback for configuration and runtime issues

### 📦 Installation Options

Users can now install CanAnnounce in multiple ways:

#### Method 1: One-Click Install
```bash
# Linux/macOS
git clone https://github.com/[username]/canannounce.git
cd canannounce
./scripts/install.sh

# Windows
git clone https://github.com/[username]/canannounce.git
cd canannounce
scripts\install.bat
```

#### Method 2: Python Package
```bash
# Web interface only
pip install canannounce

# With GUI support
pip install canannounce[gui]

# All features including development tools
pip install canannounce[gui,dev]
```

### 🐛 Bug Fixes

- Fixed assignment dates showing incorrect day due to timezone conversion
- Resolved HTML entity display in placeholder text warnings
- Fixed script path issues after reorganization
- Improved error handling for missing configuration files

### 🔄 Breaking Changes

- **Script locations changed** - Installation scripts moved from root to `scripts/` directory
- **Config file locations** - Settings now in platform-specific user directories instead of package directory
- **Updated installation commands** - Users should use new script paths or setup wizard

### 📝 Documentation Updates

- Comprehensive README with multiple installation methods
- Clear troubleshooting section
- Updated file structure documentation
- Added configuration examples and best practices

### 🚀 Migration Guide

#### For Existing Users:
1. Run `canannounce-setup` to migrate to new config location
2. Update any scripts that reference old installation file locations
3. Use new installation commands for fresh deployments

#### For New Users:
- Follow updated README installation instructions
- Use the configuration wizard for easy setup
- Choose installation method based on your needs (web-only vs GUI)

### 👥 Developer Notes

- All packaging infrastructure in place for PyPI distribution
- Cross-platform compatibility tested
- Proper Python package structure following best practices
- Ready for external contributions with clear project organization

---

**Full Changelog:** See git commit history for detailed technical changes
**Issues:** Report bugs at [GitHub Issues](https://github.com/[username]/canannounce/issues)
**Documentation:** Updated README.md with comprehensive installation guide
