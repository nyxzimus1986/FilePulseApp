"""
Command Line Interface for FilePulseApp.

This module provides the CLI functionality for the file monitoring application.
"""

import argparse
import signal
import time
import logging

from .monitor import FileMonitor, FileEvent
from .config import Config
from .output import OutputManager


class CLI:
    """Command Line Interface for FilePulseApp."""
    
    def __init__(self, config: Config):
        """Initialize CLI with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.monitor = None
        self.output_manager = OutputManager(config)
        self.running = False
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.get("output", "log_level")),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def run(self) -> None:
        """Run the CLI application."""
        self.logger.info("Starting FilePulseApp CLI")
        
        # Initialize file monitor
        monitor_config = self.config.get("monitoring")
        self.monitor = FileMonitor(self._file_event_callback, monitor_config)
        
        # Add watch directories from config
        watch_dirs = self.config.get_watch_directories()
        if not watch_dirs:
            self.logger.error("No directories to monitor. Add directories to config or use --monitor-path")
            return
        
        for directory in watch_dirs:
            if not self.monitor.add_watch_path(directory):
                self.logger.error("Failed to add watch path: %s", directory)
        
        # Start monitoring
        if not self.monitor.start_monitoring():
            self.logger.error("Failed to start file monitoring")
            return
        
        self.running = True
        self.logger.info("File monitoring started. Press Ctrl+C to stop.")
        
        try:
            # Keep the application running
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup()
    
    def _file_event_callback(self, event: FileEvent) -> None:
        """Handle file system events.
        
        Args:
            event: File system event
        """
        self.output_manager.log_event(event)
        
        # Print to console if enabled
        if self.config.get("output", "console_output"):
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event.timestamp))
            print(f"[{timestamp}] {event.event_type.upper()}: {event.file_path}")
    
    def _signal_handler(self, signum, _frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info("Received signal %s, shutting down...", signum)
        self.running = False
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        if self.monitor:
            self.monitor.stop_monitoring()
        self.logger.info("FilePulseApp CLI stopped")


def create_cli_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="FilePulseApp - File monitoring and pulse detection system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  filepulse.py --cli --monitor-path /path/to/watch
  filepulse.py --cli --config custom_config.json
  filepulse.py --cli --monitor-path /logs --config logging.json
        """
    )
    
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in command line mode"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        metavar="PATH",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--monitor-path",
        type=str,
        metavar="PATH",
        help="Path to monitor for file changes"
    )
    
    parser.add_argument(
        "--extensions",
        type=str,
        nargs="+",
        metavar="EXT",
        help="File extensions to monitor (e.g., .txt .log .json)"
    )
    
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="Monitor directories recursively (default: True)"
    )
    
    parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Do not monitor directories recursively"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--output-file",
        type=str,
        metavar="PATH",
        help="File to write monitoring output to"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="FilePulseApp 1.0.0"
    )
    
    return parser


def apply_cli_args_to_config(args: argparse.Namespace, config: Config) -> None:
    """Apply CLI arguments to configuration.
    
    Args:
        args: Parsed CLI arguments
        config: Configuration object to modify
    """
    if args.monitor_path:
        config.add_watch_directory(args.monitor_path)
    
    if args.extensions:
        config.set("monitoring", "file_extensions", args.extensions)
    
    if hasattr(args, 'recursive'):
        config.set("monitoring", "recursive", args.recursive)
    
    if args.log_level:
        config.set("output", "log_level", args.log_level)
    
    if args.output_file:
        config.set("output", "log_file", args.output_file)
    
    if args.quiet:
        config.set("output", "console_output", False)


def main():
    """Main entry point for CLI."""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if args.cli:
        cli = CLI(config_path=args.config)
        cli.run()
    else:
        # If no CLI flag, show help
        parser.print_help()
