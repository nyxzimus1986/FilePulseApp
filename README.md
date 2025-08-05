# FilePulseApp 🚀

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/Nyxzimus1986/FilePulseApp)

A modern Python application for intelligent file system monitoring with advanced system/user change separation, real-time filtering, and a beautiful GUI interface.

## ✨ Features

### 🎯 Core Functionality
- **Real-time File Monitoring**: Watch multiple directories simultaneously
- **Intelligent Classification**: Automatically separates system vs user changes
- **Advanced Filtering**: Show/hide different event types with real-time controls
- **Cross-platform**: Works on Windows, Linux, and macOS
- **Dual Interface**: Both GUI and CLI modes available

### 👤🔧 System/User Change Separation
- **Smart Detection**: Automatically classifies file events as user or system generated
- **Visual Distinction**: 👤 User changes vs 🔧 System changes with color coding
- **Configurable Patterns**: Customize detection rules via JSON configuration
- **Real-time Statistics**: Live counts of total, user, and system events

### 🖥️ Modern GUI Interface
- **Clean Design**: Modern tkinter-based interface with professional styling
- **Splash Screen**: Customizable startup experience
- **Event List**: Detailed view of all file system events with timestamps
- **Control Panel**: Easy-to-use monitoring controls and filtering options
- **Status Updates**: Real-time status bar and statistics display

### ⚙️ Configuration & Customization
- **JSON Configuration**: Flexible, user-friendly configuration system
- **Theme Support**: Multiple UI themes and customization options
- **Extension Filtering**: Monitor specific file types
- **Path Management**: Easy directory addition and removal
- **Output Options**: Configurable logging and console output

## Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Clean Launch (Recommended)
```bash
python filepulseapp.py
```
*Fast startup without splash screen - matches original FilePulse behavior*

### Full GUI Mode (With Splash)
```bash
python filepulse.py
```
*Complete experience with splash screen and animations*

### CLI Mode
```bash
python filepulse.py --cli --monitor-path /path/to/watch
```

### Windows Launchers
```bash
# Clean launcher
run_clean.bat

# Full launcher  
run_filepulse.bat
```

## Configuration

The application uses a JSON configuration file located at `~/.filepulse/config.json`. The configuration includes:

- **Monitoring settings**: File extensions, directories, recursive monitoring
- **GUI settings**: Theme, window size, splash screen options
- **Output settings**: Log levels, output formats, file destinations
- **Advanced settings**: Buffer sizes, polling intervals, performance tuning

Example configuration:
```json
{
  "monitoring": {
    "watch_directories": ["/path/to/monitor"],
    "file_extensions": [".txt", ".log", ".json"],
    "recursive": true,
    "ignore_hidden": true
  },
  "gui": {
    "theme": "default",
    "window_size": [900, 700],
    "splash_enabled": true
  },
  "output": {
    "log_level": "INFO",
    "console_output": true
  }
}
```

## Usage

### GUI Interface

1. **Start the application**: Run `python filepulse.py`
2. **Add directories**: Click "Add Directory" to select folders to monitor
3. **Start monitoring**: Click "Start Monitoring" to begin file watching
4. **View events**: File events appear in real-time in the main window
5. **Export data**: Use File → Export Events to save monitoring results

### Command Line Interface

```bash
# Monitor a specific directory
python filepulse.py --cli --monitor-path /logs

# Monitor with specific file extensions
python filepulse.py --cli --monitor-path /data --extensions .csv .json

# Set custom log level
python filepulse.py --cli --log-level DEBUG

# Output to file
python filepulse.py --cli --output-file monitoring.log
```

## Project Structure

```
FilePulseApp/
├── filepulse.py              # Main entry point
├── requirements.txt          # Dependencies
├── README.md                # Documentation
├── filepulse/               # Main package
│   ├── __init__.py          # Package initialization
│   ├── gui.py               # GUI interface
│   ├── cli.py               # Command line interface
│   ├── monitor.py           # File monitoring logic
│   ├── config.py            # Configuration management
│   ├── output.py            # Output formatting
│   ├── splash.py            # Splash screen functionality
│   ├── events.py            # Event handling system
│   ├── system_monitor.py    # System monitoring
│   └── utils.py             # Utility functions
└── .github/
    └── copilot-instructions.md  # Development guidelines
```

## Event Types

The application monitors and reports the following file events:

- **Created**: New files are detected
- **Modified**: Existing files are changed
- **Deleted**: Files are removed
- **Moved**: Files are renamed or moved

## System Requirements

- Python 3.8 or higher
- Operating System: Windows, macOS, or Linux
- Dependencies: watchdog, psutil
- Optional: PIL/Pillow for enhanced splash screens

## Development

### Setting Up Development Environment

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Code Style

This project follows PEP 8 style guidelines with:
- Type hints for function parameters and return values
- Comprehensive docstrings for all public functions
- Modular architecture with clear separation of concerns
- Error handling and logging throughout

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure all dependencies are installed with `pip install -r requirements.txt`
2. **Permission Denied**: Ensure the application has read access to monitored directories
3. **High CPU Usage**: Reduce polling frequency or limit monitored file types
4. **GUI Not Showing**: Check if tkinter is properly installed with your Python distribution

### Logging

Enable debug logging to troubleshoot issues:
```bash
python filepulse.py --cli --log-level DEBUG
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Support

For support and questions, please open an issue on the project repository.
