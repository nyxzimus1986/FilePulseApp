"""
Output management for FilePulseApp.

This module handles formatting and outputting monitoring results to various destinations.
"""

import os
import json
import csv
import logging
from typing import List, Dict, Any, Optional, TextIO
from datetime import datetime

from .monitor import FileEvent
from .config import Config


class OutputFormatter:
    """Base class for output formatters."""
    
    def format_event(self, event: FileEvent) -> str:
        """Format a file event for output.
        
        Args:
            event: File event to format
            
        Returns:
            Formatted string
        """
        raise NotImplementedError


class TextFormatter(OutputFormatter):
    """Simple text formatter."""
    
    def format_event(self, event: FileEvent) -> str:
        timestamp = datetime.fromtimestamp(event.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {event.event_type.upper()}: {event.file_path}"


class JSONFormatter(OutputFormatter):
    """JSON formatter for structured output."""
    
    def format_event(self, event: FileEvent) -> str:
        data = {
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "file_path": event.file_path,
            "iso_timestamp": datetime.fromtimestamp(event.timestamp).isoformat()
        }
        return json.dumps(data)


class CSVFormatter(OutputFormatter):
    """CSV formatter for tabular output."""
    
    def __init__(self):
        self.header_written = False
    
    def format_event(self, event: FileEvent) -> str:
        timestamp = datetime.fromtimestamp(event.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        if not self.header_written:
            header = "timestamp,event_type,file_path\n"
            self.header_written = True
            return header + f'"{timestamp}","{event.event_type}","{event.file_path}"'
        
        return f'"{timestamp}","{event.event_type}","{event.file_path}"'


class OutputManager:
    """Manages output destinations and formatting."""
    
    def __init__(self, config: Config):
        """Initialize output manager.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.log_file = None
        self.formatter = self._create_formatter()
        self.event_buffer = []
        self.buffer_size = config.get("advanced", "buffer_size") or 1000
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize log file if specified
        log_file_path = config.get("output", "log_file")
        if log_file_path:
            self._setup_log_file(log_file_path)
    
    def _create_formatter(self) -> OutputFormatter:
        """Create appropriate formatter based on configuration."""
        output_format = self.config.get("output", "format") or "text"
        
        if output_format.lower() == "json":
            return JSONFormatter()
        elif output_format.lower() == "csv":
            return CSVFormatter()
        else:
            return TextFormatter()
    
    def _setup_log_file(self, log_file_path: str) -> None:
        """Setup log file for output.
        
        Args:
            log_file_path: Path to log file
        """
        try:
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # Open log file in append mode
            self.log_file = open(log_file_path, 'a', encoding='utf-8')
            self.logger.info("Logging to file: %s", log_file_path)
        except IOError as e:
            self.logger.error("Failed to open log file %s: %s", log_file_path, e)
    
    def log_event(self, event: FileEvent) -> None:
        """Log a file event.
        
        Args:
            event: File event to log
        """
        # Add to buffer
        self.event_buffer.append(event)
        
        # Format and output
        formatted_event = self.formatter.format_event(event)
        
        # Write to log file if configured
        if self.log_file:
            try:
                self.log_file.write(formatted_event + '\n')
                self.log_file.flush()
            except IOError as e:
                self.logger.error("Failed to write to log file: %s", e)
        
        # Maintain buffer size
        if len(self.event_buffer) > self.buffer_size:
            self.event_buffer = self.event_buffer[-self.buffer_size:]
    
    def get_recent_events(self, count: int = 100) -> List[FileEvent]:
        """Get recent events from buffer.
        
        Args:
            count: Number of recent events to return
            
        Returns:
            List of recent file events
        """
        return self.event_buffer[-count:] if self.event_buffer else []
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about logged events.
        
        Returns:
            Dictionary with event statistics
        """
        if not self.event_buffer:
            return {"total_events": 0}
        
        event_types = {}
        for event in self.event_buffer:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        return {
            "total_events": len(self.event_buffer),
            "event_types": event_types,
            "first_event": self.event_buffer[0].timestamp if self.event_buffer else None,
            "last_event": self.event_buffer[-1].timestamp if self.event_buffer else None
        }
    
    def export_events(self, file_path: str, format_type: str = "json", 
                     start_time: Optional[float] = None, 
                     end_time: Optional[float] = None) -> bool:
        """Export events to file.
        
        Args:
            file_path: Path to export file
            format_type: Export format ('json', 'csv', 'txt')
            start_time: Start timestamp for filtering
            end_time: End timestamp for filtering
            
        Returns:
            True if export was successful
        """
        try:
            # Filter events by time if specified
            events_to_export = self.event_buffer
            if start_time or end_time:
                events_to_export = [
                    event for event in self.event_buffer
                    if (not start_time or event.timestamp >= start_time) and
                       (not end_time or event.timestamp <= end_time)
                ]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if format_type.lower() == "json":
                    self._export_json(f, events_to_export)
                elif format_type.lower() == "csv":
                    self._export_csv(f, events_to_export)
                else:  # default to text
                    self._export_text(f, events_to_export)
            
            self.logger.info("Exported %d events to %s", len(events_to_export), file_path)
            return True
        except IOError as e:
            self.logger.error("Failed to export events to %s: %s", file_path, e)
            return False
    
    def _export_json(self, file: TextIO, events: List[FileEvent]) -> None:
        """Export events in JSON format."""
        data = [
            {
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "file_path": event.file_path,
                "iso_timestamp": datetime.fromtimestamp(event.timestamp).isoformat()
            }
            for event in events
        ]
        json.dump(data, file, indent=2)
    
    def _export_csv(self, file: TextIO, events: List[FileEvent]) -> None:
        """Export events in CSV format."""
        writer = csv.writer(file)
        writer.writerow(["timestamp", "event_type", "file_path", "iso_timestamp"])
        
        for event in events:
            iso_timestamp = datetime.fromtimestamp(event.timestamp).isoformat()
            writer.writerow([event.timestamp, event.event_type, event.file_path, iso_timestamp])
    
    def _export_text(self, file: TextIO, events: List[FileEvent]) -> None:
        """Export events in text format."""
        text_formatter = TextFormatter()
        for event in events:
            file.write(text_formatter.format_event(event) + '\n')
    
    def close(self) -> None:
        """Close output manager and clean up resources."""
        if self.log_file:
            self.log_file.close()
            self.log_file = None
    
    def __del__(self):
        """Destructor to ensure resources are cleaned up."""
        self.close()
