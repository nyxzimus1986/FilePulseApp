# Copilot Instructions for FilePulseApp

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
FilePulseApp is a Python application for file monitoring and pulse detection with:
- GUI interface using tkinter/customtkinter
- File system monitoring capabilities
- Splash screen functionality
- CLI interface
- Configuration management
- System monitoring features

## Development Guidelines
- Use Python 3.8+ compatible code
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Implement proper error handling and logging
- Create modular, reusable components
- Use appropriate design patterns for GUI and monitoring
- Include docstrings for all classes and functions

## Architecture
- `filepulse/` - Main package directory
- `gui.py` - Main GUI interface
- `monitor.py` - File monitoring logic
- `splash.py` - Splash screen functionality
- `cli.py` - Command line interface
- `config.py` - Configuration management
- `utils.py` - Utility functions
- `events.py` - Event handling system
- `output.py` - Output formatting and handling

## Dependencies
- Focus on standard library when possible
- Use `watchdog` for file monitoring
- Use `tkinter` or `customtkinter` for GUI
- Use `argparse` for CLI
- Use `configparser` or `json` for configuration
