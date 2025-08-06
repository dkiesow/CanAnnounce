#!/usr/bin/env python3
from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Canvas announcements automation tool"

setup(
    name="canannounce",
    version="1.0.0",
    description="Canvas announcements automation tool with web interface",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Damon Kiesow",
    author_email="damon@kiesow.net",
    url="https://github.com/dkiesow/canannounce",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "canannounce": [
            "web/templates/*.html",
            "web/static/*.css",
            "config/local_settings_template.py",
        ],
    },
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.25.0",
        "PyPDF2>=3.0.0",
    ],
    extras_require={
        "gui": [
            "PyQt6>=6.0.0",
            # OR "PyQt5>=5.15.0" if you prefer Qt5
        ],
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "canannounce=canannounce.main_web:main",
            "canannounce-setup=canannounce.config.setup_config:setup_config",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="canvas lms announcements automation education",
)
