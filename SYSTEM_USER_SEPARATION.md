# FilePulseApp - System/User Change Separation

## Overview
FilePulseApp now includes intelligent separation of system-generated changes from user-generated changes, providing better insight into file system activity.

## Features Implemented

### 1. Enhanced File Event Classification
- **FileEvent Class**: Enhanced with source type classification
- **Automatic Detection**: Files are automatically classified as "system" or "user" based on:
  - File name patterns (thumbs.db, .tmp, ~$, .cache, etc.)
  - Directory paths (AppData, System32, __pycache__, .git, etc.)
- **Configurable Patterns**: System patterns are configurable via JSON config

### 2. Visual Distinction
- **Icons**: 👤 for user changes, 🔧 for system changes
- **Color Coding**: Different visual styling in the GUI
- **Event Display**: Clear indication of source type in event list

### 3. Filtering Controls
- **Show/Hide Options**: Separate checkboxes for system and user changes
- **Real-time Filtering**: Changes apply immediately to displayed events
- **Statistics Display**: Live counts of total, user, and system events

### 4. Configuration Options
```json
{
  "filtering": {
    "show_system_changes": true,
    "show_user_changes": true,
    "separate_system_user": true,
    "system_file_patterns": [
      "thumbs.db", "desktop.ini", ".ds_store", "~$", ".tmp", 
      ".temp", ".swp", ".bak", ".cache", ".log", ".pid", ".lock"
    ],
    "system_directories": [
      "appdata", "programdata", "windows", "system32", 
      "program files", "recycle", "temp", "tmp", "__pycache__",
      ".vscode", ".idea", ".git", ".svn"
    ]
  }
}
```

## Usage Examples

### 1. Running the Application
```bash
# Full GUI with splash screen
python filepulse.py

# Clean launcher
python filepulseapp.py

# Demo with information
python demo_filtering.py

# Test classification system
python test_filtering.py
```

### 2. GUI Operations
1. **Add Directories**: Click "Add Directory" to select folders to monitor
2. **Start Monitoring**: Click "Start Monitoring" to begin file watching
3. **Filter Events**: Use checkboxes to show/hide system vs user changes
4. **View Statistics**: Monitor live event counts in the control panel

### 3. File Classification Examples
- **User Changes**: 👤
  - Documents: `C:/Users/test/Documents/report.txt`
  - Code files: `C:/projects/myapp/src/main.py`
  - Desktop files: `C:/Users/test/Desktop/notes.md`

- **System Changes**: 🔧
  - Temp files: `C:/Users/test/AppData/Local/Temp/temp123.tmp`
  - Cache files: `C:/Users/test/Documents/Thumbs.db`
  - Office temp: `C:/Users/test/Desktop/~$document.docx`
  - System libraries: `C:/Windows/System32/something.dll`
  - Git files: `C:/projects/myapp/.git/refs/heads/main`
  - Python cache: `C:/projects/myapp/__pycache__/module.pyc`
  - IDE config: `C:/projects/myapp/.vscode/settings.json`

## Technical Implementation

### Enhanced FileEvent Class
```python
class FileEvent:
    def __init__(self, event_type: str, file_path: str, timestamp: float = None, 
                 source_type: str = None, full_config: dict = None):
        self.source_type = source_type or self._classify_source(file_path)
    
    def is_system_change(self) -> bool:
        return self.source_type == 'system'
    
    def is_user_change(self) -> bool:
        return self.source_type == 'user'
```

### FileMonitor with Filtering
```python
class FileMonitor:
    def __init__(self, callback, config=None, full_config=None):
        self.filtering_config = full_config.get('filtering') if full_config else {}
        self.show_system_changes = self.filtering_config.get('show_system_changes', True)
        self.show_user_changes = self.filtering_config.get('show_user_changes', True)
    
    def set_filtering_options(self, show_system: bool, show_user: bool, separate: bool):
        # Update filtering options dynamically
```

### GUI Enhancements
- **ControlPanel**: Added filtering checkboxes and statistics display
- **EventList**: Enhanced with visual distinction and source icons
- **Real-time Updates**: Statistics and filtering update immediately

## Benefits

1. **Reduced Noise**: Filter out system-generated events to focus on user actions
2. **Better Debugging**: Distinguish between intentional changes and automatic system operations
3. **Improved Monitoring**: Clearer understanding of file system activity patterns
4. **Configurable**: Customize patterns and directories based on specific needs
5. **Real-time**: Immediate feedback and statistics updates

## Next Steps

The system/user change separation is now fully implemented and functional. You can:

1. Run `python demo_filtering.py` to see the enhanced GUI
2. Run `python test_filtering.py` to test the classification system
3. Customize the filtering patterns in the configuration
4. Monitor different directories to see the classification in action

The FilePulseApp now provides intelligent file system monitoring with clear distinction between system and user activities!
