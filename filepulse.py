#!/usr/bin/env python3
"""
FilePulseApp - Main entry point for the application.

This script provides the main entry point for the FilePulseApp file monitoring system.
It can be run directly or imported as a module.
"""

import sys
import os
import argparse

# Add the package to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from filepulse.gui import FilePulseGUI
from filepulse.cli import CLI
from filepulse.config import Config


def main():
    """Main entry point for the FilePulseApp."""
    parser = argparse.ArgumentParser(
        description="FilePulseApp - File monitoring and pulse detection system"
    )
    parser.add_argument(
        "--cli", 
        action="store_true", 
        help="Run in command line mode"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to configuration file"
    )
    parser.add_argument(
        "--monitor-path", 
        type=str, 
        help="Path to monitor for file changes"
    )
    parser.add_argument(
        "--no-splash", 
        action="store_true", 
        help="Skip splash screen"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config(args.config)
    
    if args.cli:
        # Run in CLI mode
        cli = CLI(config)
        cli.run()
    else:
        # Run in GUI mode
        gui = FilePulseGUI(config, show_splash=not args.no_splash)
        gui.run()


if __name__ == "__main__":
    main()
