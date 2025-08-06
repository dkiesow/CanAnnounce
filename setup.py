#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="canannounce",
    version="0.1.0",
    description="Canvas announcements automation tool",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "flask",
        "requests",
        "PyPDF2",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "canannounce=canannounce.main:main",
            "canannounce-web=canannounce.main_web:main",
        ],
    },
)
