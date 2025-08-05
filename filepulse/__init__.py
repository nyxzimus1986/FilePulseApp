"""
FilePulseApp - A Python application for file monitoring and pulse detection.

This package provides file system monitoring capabilities with a modern GUI interface,
splash screens, CLI support, and comprehensive configuration management.
"""

__version__ = "1.0.0"
__author__ = "FilePulse Development Team"

from .gui import FilePulseGUI
from .monitor import FileMonitor
from .config import Config
from .cli import CLI

__all__ = ['FilePulseGUI', 'FileMonitor', 'Config', 'CLI']
