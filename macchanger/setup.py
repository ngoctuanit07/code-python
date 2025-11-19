# File: setup.py
from setuptools import setup, find_packages

setup(
    name="macchanger-tool",
    version="0.1.0",
    description="Cross-platform MAC address changer (Linux/macOS/Windows)",
    packages=find_packages(),
    python_requires=">=3.11",
    entry_points={"console_scripts": ["macchanger=macchanger.cli:main"]},
)
