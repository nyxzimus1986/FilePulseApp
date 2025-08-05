#!/usr/bin/env python3
"""
Test script to demonstrate system/user change separation in FilePulseApp.
"""

import os
import sys
import time
from pathlib import Path

# Add the package to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from filepulse.monitor import FileEvent
from filepulse.config import Config


def test_file_classification():
    """Test the file event classification system."""
    print("Testing FilePulseApp System/User Change Classification")
    print("=" * 55)
    
    # Create config
    config = Config()
    
    # Test various file paths
    test_files = [
        # User files
        ("C:/Users/test/Documents/report.txt", "User document"),
        ("C:/Users/test/Desktop/notes.md", "User desktop file"),
        ("C:/projects/myapp/src/main.py", "User source code"),
        
        # System files
        ("C:/Users/test/AppData/Local/Temp/temp123.tmp", "System temp file"),
        ("C:/Users/test/Documents/Thumbs.db", "System thumbnail cache"),
        ("C:/Users/test/Desktop/~$document.docx", "Office temp file"),
        ("C:/Windows/System32/something.dll", "System library"),
        ("C:/projects/myapp/.git/refs/heads/main", "Git system file"),
        ("C:/projects/myapp/__pycache__/module.pyc", "Python cache file"),
        ("C:/projects/myapp/.vscode/settings.json", "VS Code config"),
    ]
    
    print("File Classification Results:")
    print("-" * 80)
    print(f"{'File Path':<50} {'Type':<8} {'Description'}")
    print("-" * 80)
    
    for file_path, description in test_files:
        # Create FileEvent with full config
        event = FileEvent(
            event_type='created',
            file_path=file_path,
            full_config=config.config
        )
        
        source_type = "System" if event.is_system_change() else "User"
        icon = "🔧" if event.is_system_change() else "👤"
        
        print(f"{file_path:<50} {icon} {source_type:<7} {description}")
    
    print("-" * 80)
    print("\nFiltering Configuration:")
    filtering_config = config.get('filtering')
    print(f"  System file patterns: {len(filtering_config['system_file_patterns'])} patterns")
    print(f"  System directories: {len(filtering_config['system_directories'])} directories")
    print(f"  Separation enabled: {filtering_config['separate_system_user']}")
    
    print("\nTo see this in action:")
    print("1. Run: python filepulse.py")
    print("2. Add a directory to monitor")
    print("3. Use the filtering checkboxes to show/hide different event types")
    print("4. Create/modify files and observe the different icons:")
    print("   👤 = User-generated changes")
    print("   🔧 = System-generated changes") 


if __name__ == "__main__":
    test_file_classification()
