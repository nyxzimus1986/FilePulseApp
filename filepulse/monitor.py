"""
File monitoring functionality for FilePulseApp.

This module provides file system monitoring capabilities using the watchdog library.
"""

import os
import time
from datetime import datetime
from typing import List, Callable, Set
from threading import Thread, Event
import logging

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog library not available. Using polling-based monitoring.")


class FileEvent:
    """Represents a file system event with source classification."""
    
    def __init__(self, event_type: str, file_path: str, timestamp: float = None, source_type: str = None, full_config: dict = None):
        self.event_type = event_type  # 'created', 'modified', 'deleted', 'moved'
        self.file_path = file_path
        self.timestamp = timestamp or time.time()
        self.full_config = full_config
        self.source_type = source_type or self._classify_source(file_path)
    
    def _classify_source(self, file_path: str) -> str:
        """Classify if this is a system or user change based on file patterns."""
        
        # Get file/directory name and path components
        file_name = os.path.basename(file_path).lower()
        dir_path = os.path.dirname(file_path).lower()
        
        # Get patterns from config if available
        if self.full_config and 'filtering' in self.full_config:
            filtering_config = self.full_config['filtering']
            system_patterns = [p.lower() for p in filtering_config.get('system_file_patterns', [])]
            system_dirs = [d.lower() for d in filtering_config.get('system_directories', [])]
        else:
            # Fallback patterns if no config
            system_patterns = [
                # Windows system files
                'thumbs.db', 'desktop.ini', 'folder.ico', '.ds_store',
                # Temporary files
                '~$', '.tmp', '.temp', '.swp', '.bak',
                # System directories
                '$recycle.bin', 'system volume information',
                # Browser cache
                '.cache', 'cache', 'temp',
                # IDE/Editor files
                '.vscode', '.idea', '__pycache__', '.git', '.svn',
                # Log files (often system generated)
                '.log', '.pid', '.lock'
            ]
            system_dirs = [
                'appdata', 'programdata', 'windows', 'system32',
                'program files', 'recycle', 'temp', 'tmp'
            ]
        
        # Check if file matches system patterns
        for pattern in system_patterns:
            if pattern in file_name or pattern in dir_path:
                return 'system'
        
        # Check for system directories in path
        for sys_dir in system_dirs:
            if sys_dir in dir_path:
                return 'system'
        
        # Default to user change
        return 'user'
    
    def is_system_change(self) -> bool:
        """Check if this is a system-generated change."""
        return self.source_type == 'system'
    
    def is_user_change(self) -> bool:
        """Check if this is a user-generated change."""
        return self.source_type == 'user'
    
    def __str__(self) -> str:
        source_icon = "🔧" if self.is_system_change() else "👤"
        return f"{source_icon} {self.event_type}: {self.file_path}"


class FilePulseEventHandler(FileSystemEventHandler):
    """Custom event handler for file system events."""
    
    def __init__(self, callback: Callable[[FileEvent], None], file_extensions: Set[str] = None, full_config: dict = None):
        super().__init__()
        self.callback = callback
        self.file_extensions = file_extensions or set()
        self.full_config = full_config
        self.logger = logging.getLogger(__name__)
    
    def _should_process(self, file_path: str) -> bool:
        """Check if file should be processed based on extensions."""
        if not self.file_extensions:
            return True
        return any(file_path.lower().endswith(ext.lower()) for ext in self.file_extensions)
    
    def on_created(self, event):
        if not event.is_directory and self._should_process(event.src_path):
            file_event = FileEvent(
                event_type='created',
                file_path=event.src_path,
                timestamp=datetime.now().timestamp(),
                full_config=self.full_config
            )
            self.callback(file_event)
    
    def on_modified(self, event):
        if not event.is_directory and self._should_process(event.src_path):
            file_event = FileEvent(
                event_type='modified',
                file_path=event.src_path,
                timestamp=datetime.now().timestamp(),
                full_config=self.full_config
            )
            self.callback(file_event)
    
    def on_deleted(self, event):
        if not event.is_directory and self._should_process(event.src_path):
            file_event = FileEvent(
                event_type='deleted',
                file_path=event.src_path,
                timestamp=datetime.now().timestamp(),
                full_config=self.full_config
            )
            self.callback(file_event)
    
    def on_moved(self, event):
        if not event.is_directory and self._should_process(event.dest_path):
            file_event = FileEvent(
                event_type='moved',
                file_path=event.dest_path,
                timestamp=datetime.now().timestamp(),
                full_config=self.full_config
            )
            self.callback(file_event)


class PollingMonitor:
    """Fallback polling-based file monitor when watchdog is not available."""
    
    def __init__(self, callback: Callable[[FileEvent], None], file_extensions: Set[str] = None, full_config: dict = None):
        self.callback = callback
        self.file_extensions = file_extensions or set()
        self.full_config = full_config
        self.file_states = {}
        self.running = False
        self.thread = None
        self.stop_event = Event()
        self.polling_interval = 1.0
    
    def start_monitoring(self, paths: List[str]) -> None:
        """Start polling-based monitoring."""
        self.running = True
        self.stop_event.clear()
        self.thread = Thread(target=self._monitor_loop, args=(paths,))
        self.thread.daemon = True
        self.thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop polling-based monitoring."""
        self.running = False
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=2.0)
    
    def _monitor_loop(self, paths: List[str]) -> None:
        """Main monitoring loop."""
        while self.running and not self.stop_event.is_set():
            for path in paths:
                if os.path.exists(path):
                    self._scan_directory(path)
            self.stop_event.wait(self.polling_interval)
    
    def _scan_directory(self, directory: str) -> None:
        """Scan directory for changes."""
        try:
            for root, _dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self._should_process(file_path):
                        self._check_file_changes(file_path)
        except (OSError, PermissionError):
            pass  # Skip inaccessible directories
    
    def _should_process(self, file_path: str) -> bool:
        """Check if file should be processed based on extensions."""
        if not self.file_extensions:
            return True
        return any(file_path.lower().endswith(ext.lower()) for ext in self.file_extensions)
    
    def _check_file_changes(self, file_path: str) -> None:
        """Check if file has changed since last scan."""
        try:
            stat = os.stat(file_path)
            current_state = (stat.st_mtime, stat.st_size)
            
            if file_path not in self.file_states:
                self.file_states[file_path] = current_state
                file_event = FileEvent(
                    event_type='created',
                    file_path=file_path,
                    timestamp=datetime.now().timestamp(),
                    full_config=self.full_config
                )
                self.callback(file_event)
            elif self.file_states[file_path] != current_state:
                self.file_states[file_path] = current_state
                file_event = FileEvent(
                    event_type='modified',
                    file_path=file_path,
                    timestamp=datetime.now().timestamp(),
                    full_config=self.full_config
                )
                self.callback(file_event)
        except (OSError, PermissionError):
            # File might have been deleted
            if file_path in self.file_states:
                del self.file_states[file_path]
                self.callback(FileEvent('deleted', file_path))


class FileMonitor:
    """Main file monitoring class with system/user change separation."""
    
    def __init__(self, callback: Callable[[FileEvent], None], config: dict = None, full_config=None):
        """Initialize file monitor.
        
        Args:
            callback: Function to call when file events occur
            config: Configuration dictionary for monitoring settings
            full_config: Full configuration object for filtering settings
        """
        self.callback = callback
        self.config = config or {}
        self.full_config = full_config
        self.file_extensions = set(self.config.get('file_extensions', []))
        self.recursive = self.config.get('recursive', True)
        self.ignore_hidden = self.config.get('ignore_hidden', True)
        
        # Filtering configuration
        self.filtering_config = full_config.get('filtering') if full_config else {}
        self.show_system_changes = self.filtering_config.get('show_system_changes', True)
        self.show_user_changes = self.filtering_config.get('show_user_changes', True)
        self.separate_system_user = self.filtering_config.get('separate_system_user', True)
        
        self.observer = None
        self.polling_monitor = None
        self.is_monitoring = False
        self.watched_paths = []
        
        # Statistics
        self.stats = {
            'total_events': 0,
            'user_events': 0,
            'system_events': 0
        }
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def add_watch_path(self, path: str) -> bool:
        """Add a path to monitor.
        
        Args:
            path: Path to monitor
            
        Returns:
            True if path was added successfully
        """
        if not os.path.exists(path):
            self.logger.error("Path does not exist: %s", path)
            return False
        
        if path not in self.watched_paths:
            self.watched_paths.append(path)
            if self.is_monitoring:
                self._add_watch_to_observer(path)
            return True
        return False
    
    def remove_watch_path(self, path: str) -> bool:
        """Remove a path from monitoring.
        
        Args:
            path: Path to stop monitoring
            
        Returns:
            True if path was removed successfully
        """
        if path in self.watched_paths:
            self.watched_paths.remove(path)
            # Note: watchdog doesn't provide easy way to remove single watch
            # For now, we'll restart monitoring if needed
            return True
        return False
    
    def start_monitoring(self) -> bool:
        """Start monitoring all watched paths.
        
        Returns:
            True if monitoring started successfully
        """
        if self.is_monitoring:
            return True
        
        if not self.watched_paths:
            self.logger.warning("No paths to monitor")
            return False
        
        if WATCHDOG_AVAILABLE:
            return self._start_watchdog_monitoring()
        else:
            return self._start_polling_monitoring()
    
    def stop_monitoring(self) -> None:
        """Stop monitoring all paths."""
        if not self.is_monitoring:
            return
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        if self.polling_monitor:
            self.polling_monitor.stop_monitoring()
            self.polling_monitor = None
        
        self.is_monitoring = False
        self.logger.info("File monitoring stopped")
    
    def _start_watchdog_monitoring(self) -> bool:
        """Start watchdog-based monitoring."""
        try:
            self.observer = Observer()
            
            # Create callback wrapper for filtering
            filtered_callback = self._create_filtered_callback()
            
            event_handler = FilePulseEventHandler(
                callback=filtered_callback,
                file_extensions=self.file_extensions,
                full_config=self.full_config
            )
            
            for path in self.watched_paths:
                self.observer.schedule(event_handler, path, recursive=self.recursive)
            
            self.observer.start()
            self.is_monitoring = True
            self.logger.info("Started watchdog monitoring for %d paths", len(self.watched_paths))
            return True
        except (OSError, RuntimeError) as e:
            self.logger.error("Failed to start watchdog monitoring: %s", e)
            return False
    
    def _start_polling_monitoring(self) -> bool:
        """Start polling-based monitoring."""
        try:
            # Create callback wrapper for filtering
            filtered_callback = self._create_filtered_callback()
            
            self.polling_monitor = PollingMonitor(
                callback=filtered_callback,
                file_extensions=self.file_extensions,
                full_config=self.full_config
            )
            self.polling_monitor.start_monitoring(self.watched_paths)
            self.is_monitoring = True
            self.logger.info("Started polling monitoring for %d paths", len(self.watched_paths))
            return True
        except (OSError, RuntimeError) as e:
            self.logger.error("Failed to start polling monitoring: %s", e)
            return False
    
    def _create_filtered_callback(self) -> Callable[[FileEvent], None]:
        """Create a callback wrapper that applies filtering rules.
        
        Returns:
            Filtered callback function
        """
        def filtered_callback(file_event: FileEvent) -> None:
            """Apply filtering rules before calling the original callback."""
            # Update statistics
            self.stats['total_events'] += 1
            if file_event.is_system_change():
                self.stats['system_events'] += 1
            else:
                self.stats['user_events'] += 1
            
            # Apply filtering based on configuration
            if self.separate_system_user:
                # If separation is enabled, filter based on show settings
                if file_event.is_system_change() and not self.show_system_changes:
                    return
                if file_event.is_user_change() and not self.show_user_changes:
                    return
            
            # Call the original callback with the filtered event
            self.callback(file_event)
        
        return filtered_callback
    
    def get_stats(self) -> dict:
        """Get monitoring statistics.
        
        Returns:
            Dictionary containing monitoring statistics
        """
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Reset monitoring statistics."""
        self.stats = {
            'total_events': 0,
            'user_events': 0,
            'system_events': 0
        }
    
    def set_filtering_options(self, show_system: bool = True, show_user: bool = True, separate: bool = True) -> None:
        """Update filtering options dynamically.
        
        Args:
            show_system: Whether to show system-generated changes
            show_user: Whether to show user-generated changes
            separate: Whether to enable system/user separation
        """
        self.show_system_changes = show_system
        self.show_user_changes = show_user
        self.separate_system_user = separate
        self.logger.info("Updated filtering: system=%s, user=%s, separate=%s", show_system, show_user, separate)
    
    def _add_watch_to_observer(self, path: str) -> None:
        """Add watch to existing observer."""
        if self.observer:
            event_handler = FilePulseEventHandler(self.callback, self.file_extensions)
            self.observer.schedule(event_handler, path, recursive=self.recursive)
    
    def get_status(self) -> dict:
        """Get monitoring status information.
        
        Returns:
            Dictionary with status information
        """
        return {
            'monitoring': self.is_monitoring,
            'watched_paths': len(self.watched_paths),
            'method': 'watchdog' if WATCHDOG_AVAILABLE else 'polling',
            'paths': self.watched_paths.copy()
        }
