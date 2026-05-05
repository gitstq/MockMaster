#!/usr/bin/env python3
"""
MockMaster - API Mock Server Intelligent Manager
Setup configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

setup(
    name="mockmaster",
    version="1.0.0",
    author="MockMaster Team",
    author_email="mockmaster@example.com",
    description="API Mock Server Intelligent Manager - Zero-dependency CLI tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mockmaster",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing :: Mocking",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "mockmaster=mockmaster.cli:main",
            "mm=mockmaster.cli:main",
        ],
    },
    keywords=[
        "mock",
        "api",
        "server",
        "testing",
        "development",
        "cli",
        "http",
        "rest",
        "zero-dependency"
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/mockmaster/issues",
        "Source": "https://github.com/yourusername/mockmaster",
        "Documentation": "https://github.com/yourusername/mockmaster#readme",
    },
)