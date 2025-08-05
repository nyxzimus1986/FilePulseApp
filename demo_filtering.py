#!/usr/bin/env python3
"""
Demo launcher for FilePulseApp with system/user change separation.
"""

import sys
import os

# Add the package to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from filepulse.gui import FilePulseGUI
from filepulse.config import Config


def main():
    """Launch the GUI with enhanced filtering."""
    print("FilePulseApp - System/User Change Separation Demo")
    print("=" * 50)
    print()
    print("Features:")
    print("- 👤 User-generated changes (documents, code, etc.)")
    print("- 🔧 System-generated changes (cache, temp, logs, etc.)")
    print("- Real-time filtering with checkboxes")
    print("- Statistics display showing event counts")
    print("- Visual distinction in the event list")
    print()
    print("Usage:")
    print("1. Add directories to monitor")
    print("2. Start monitoring")
    print("3. Use filter checkboxes to show/hide event types")
    print("4. Create/modify files to see classification in action")
    print()
    
    try:
        # Create configuration
        config = Config()
        
        # Launch GUI
        gui = FilePulseGUI(config, show_splash=True)
        gui.run()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
