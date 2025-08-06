"""
Event handling system for FilePulseApp.

This module provides event handling and notification capabilities.
"""

import threading
import time
from typing import Any, Callable, Dict, Optional, Set
from enum import Enum
import logging
from dataclasses import dataclass
from collections import defaultdict


class EventType(Enum):
    """Event types for the application."""
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    FILE_MOVED = "file_moved"
    MONITORING_STARTED = "monitoring_started"
    MONITORING_STOPPED = "monitoring_stopped"
    ERROR_OCCURRED = "error_occurred"
    CONFIG_CHANGED = "config_changed"
    APPLICATION_STARTED = "application_started"
    APPLICATION_STOPPED = "application_stopped"


@dataclass
class Event:
    """Event data structure."""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: float
    source: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class EventHandler:
    """Base class for event handlers."""
    
    def handle_event(self, event: Event) -> None:
        """Handle an event.
        
        Args:
            event: Event to handle
        """
        raise NotImplementedError
    
    def can_handle(self, _event_type: EventType) -> bool:
        """Check if this handler can handle the given event type.
        
        Args:
            event_type: Event type to check
            
        Returns:
            True if this handler can handle the event type
        """
        return True


class FunctionEventHandler(EventHandler):
    """Event handler that wraps a function."""
    
    def __init__(self, handler_func: Callable[[Event], None], 
                 event_types: Optional[Set[EventType]] = None):
        """Initialize function event handler.
        
        Args:
            handler_func: Function to call for events
            event_types: Set of event types this handler accepts (None for all)
        """
        self.handler_func = handler_func
        self.event_types = event_types
    
    def handle_event(self, event: Event) -> None:
        """Handle event by calling the wrapped function."""
        try:
            self.handler_func(event)
        except (OSError, RuntimeError) as e:
            logging.getLogger(__name__).error("Error in event handler: %s", e)
    
    def can_handle(self, event_type: EventType) -> bool:
        """Check if this handler can handle the given event type."""
        return self.event_types is None or event_type in self.event_types


class LoggingEventHandler(EventHandler):
    """Event handler that logs events."""
    
    def __init__(self, logger: Optional[logging.Logger] = None, 
                 log_level: int = logging.INFO):
        """Initialize logging event handler.
        
        Args:
            logger: Logger to use (None for default)
            log_level: Log level for events
        """
        self.logger = logger or logging.getLogger(__name__)
        self.log_level = log_level
    
    def handle_event(self, event: Event) -> None:
        """Log the event."""
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event.timestamp))
        message = f"[{timestamp_str}] {event.event_type.value}: {event.data}"
        if event.source:
            message += f" (source: {event.source})"
        
        self.logger.log(self.log_level, message)


class EventFilter:
    """Base class for event filters."""
    
    def should_process(self, event: Event) -> bool:
        """Check if event should be processed.
        
        Args:
            event: Event to check
            
        Returns:
            True if event should be processed
        """
        raise NotImplementedError


class EventTypeFilter(EventFilter):
    """Filter events by type."""
    
    def __init__(self, allowed_types: Set[EventType]):
        """Initialize event type filter.
        
        Args:
            allowed_types: Set of allowed event types
        """
        self.allowed_types = allowed_types
    
    def should_process(self, event: Event) -> bool:
        """Check if event type is allowed."""
        return event.event_type in self.allowed_types


class SourceFilter(EventFilter):
    """Filter events by source."""
    
    def __init__(self, allowed_sources: Set[str]):
        """Initialize source filter.
        
        Args:
            allowed_sources: Set of allowed sources
        """
        self.allowed_sources = allowed_sources
    
    def should_process(self, event: Event) -> bool:
        """Check if event source is allowed."""
        return event.source is None or event.source in self.allowed_sources


class TimeWindowFilter(EventFilter):
    """Filter events by time window."""
    
    def __init__(self, window_seconds: float):
        """Initialize time window filter.
        
        Args:
            window_seconds: Time window in seconds
        """
        self.window_seconds = window_seconds
        self.last_events = defaultdict(float)
    
    def should_process(self, event: Event) -> bool:
        """Check if event is outside the time window for deduplication."""
        key = (event.event_type, str(event.data))
        last_time = self.last_events.get(key, 0)
        
        if event.timestamp - last_time < self.window_seconds:
            return False
        
        self.last_events[key] = event.timestamp
        return True


class EventBus:
    """Central event bus for the application."""
    
    def __init__(self):
        """Initialize event bus."""
        self.handlers = []
        self.filters = []
        self.running = False
        self.event_queue = []
        self.queue_lock = threading.Lock()
        self.processing_thread = None
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            'events_published': 0,
            'events_processed': 0,
            'events_filtered': 0,
            'handler_errors': 0
        }
    
    def add_handler(self, handler: EventHandler) -> None:
        """Add event handler.
        
        Args:
            handler: Event handler to add
        """
        if handler not in self.handlers:
            self.handlers.append(handler)
            self.logger.debug("Added event handler: %s", type(handler).__name__)
    
    def remove_handler(self, handler: EventHandler) -> None:
        """Remove event handler.
        
        Args:
            handler: Event handler to remove
        """
        if handler in self.handlers:
            self.handlers.remove(handler)
            self.logger.debug("Removed event handler: %s", type(handler).__name__)
    
    def add_filter(self, event_filter: EventFilter) -> None:
        """Add event filter.
        
        Args:
            event_filter: Event filter to add
        """
        if event_filter not in self.filters:
            self.filters.append(event_filter)
            self.logger.debug("Added event filter: %s", type(event_filter).__name__)
    
    def remove_filter(self, event_filter: EventFilter) -> None:
        """Remove event filter.
        
        Args:
            event_filter: Event filter to remove
        """
        if event_filter in self.filters:
            self.filters.remove(event_filter)
            self.logger.debug("Removed event filter: %s", type(event_filter).__name__)
    
    def publish(self, event: Event) -> None:
        """Publish an event.
        
        Args:
            event: Event to publish
        """
        with self.queue_lock:
            self.event_queue.append(event)
            self.stats['events_published'] += 1
    
    def publish_event(self, event_type: EventType, data: Dict[str, Any], 
                     source: Optional[str] = None) -> None:
        """Publish an event with given parameters.
        
        Args:
            event_type: Type of event
            data: Event data
            source: Optional event source
        """
        event = Event(event_type, data, time.time(), source)
        self.publish(event)
    
    def start_processing(self) -> None:
        """Start event processing in background thread."""
        if self.running:
            return
        
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_events_loop, daemon=True)
        self.processing_thread.start()
        self.logger.info("Event bus started")
    
    def stop_processing(self) -> None:
        """Stop event processing."""
        if not self.running:
            return
        
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)
        self.logger.info("Event bus stopped")
    
    def _process_events_loop(self) -> None:
        """Main event processing loop."""
        while self.running:
            events_to_process = []
            
            # Get events from queue
            with self.queue_lock:
                if self.event_queue:
                    events_to_process = self.event_queue.copy()
                    self.event_queue.clear()
            
            # Process events
            for event in events_to_process:
                self._process_event(event)
            
            # Small delay to prevent busy waiting
            time.sleep(0.01)
    
    def _process_event(self, event: Event) -> None:
        """Process a single event.
        
        Args:
            event: Event to process
        """
        try:
            # Apply filters
            for event_filter in self.filters:
                if not event_filter.should_process(event):
                    self.stats['events_filtered'] += 1
                    return
            
            # Send to handlers
            for handler in self.handlers:
                if handler.can_handle(event.event_type):
                    try:
                        handler.handle_event(event)
                    except (OSError, RuntimeError) as e:
                        self.stats['handler_errors'] += 1
                        self.logger.error("Error in event handler %s: %s", type(handler).__name__, e)
            
            self.stats['events_processed'] += 1
            
        except (OSError, RuntimeError) as e:
            self.logger.error("Error processing event %s: %s", event.event_type, e)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.queue_lock:
            queue_size = len(self.event_queue)
        
        return {
            **self.stats,
            'queue_size': queue_size,
            'handlers_count': len(self.handlers),
            'filters_count': len(self.filters),
            'running': self.running
        }
    
    def clear_statistics(self) -> None:
        """Clear event bus statistics."""
        self.stats = {
            'events_published': 0,
            'events_processed': 0,
            'events_filtered': 0,
            'handler_errors': 0
        }


# Global event bus instance
_global_event_bus = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance.
    
    Returns:
        Global EventBus instance
    """
    # global _global_event_bus  # Removed for lint compliance
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def publish_event(event_type: EventType, data: Dict[str, Any], 
                 source: Optional[str] = None) -> None:
    """Publish event to global event bus.
    
    Args:
        event_type: Type of event
        data: Event data
        source: Optional event source
    """
    get_event_bus().publish_event(event_type, data, source)


def add_event_handler(handler: EventHandler) -> None:
    """Add event handler to global event bus.
    
    Args:
        handler: Event handler to add
    """
    get_event_bus().add_handler(handler)


def add_function_handler(handler_func: Callable[[Event], None], 
                        event_types: Optional[Set[EventType]] = None) -> None:
    """Add function as event handler to global event bus.
    
    Args:
        handler_func: Function to call for events
        event_types: Set of event types this handler accepts (None for all)
    """
    handler = FunctionEventHandler(handler_func, event_types)
    add_event_handler(handler)


def start_event_processing() -> None:
    """Start global event bus processing."""
    get_event_bus().start_processing()


def stop_event_processing() -> None:
    """Stop global event bus processing."""
    get_event_bus().stop_processing()
