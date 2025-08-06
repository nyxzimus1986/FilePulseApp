"""
Utility functions for FilePulseApp.

This module provides common utility functions used throughout the application.
"""

import os
import sys
import re
import hashlib
import json
from typing import Any, Dict, List, Optional
import logging


def get_file_size_formatted(file_path: str) -> str:
    """Get human-readable file size.
    
    Args:
        file_path: Path to file
        
    Returns:
        Formatted file size string
    """
    try:
        size = os.path.getsize(file_path)
        return format_bytes(size)
    except (OSError, IOError):
        return "Unknown"


def format_bytes(size: int) -> str:
    """Format bytes into human-readable string.
    
    Args:
        size: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    import math
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return f"{s} {size_names[i]}"


def parse_size_string(size_str: str) -> int:
    """Parse size string into bytes.
    
    Args:
        size_str: Size string like "10MB", "1.5GB", etc.
        
    Returns:
        Size in bytes
    """
    size_str = size_str.upper().strip()
    
    # Extract number and unit
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGTPE]?B?)$', size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
    
    number, unit = match.groups()
    number = float(number)
    
    # Convert to bytes
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4,
        'PB': 1024**5,
        'EB': 1024**6
    }
    
    if unit == '':
        unit = 'B'
    elif unit == 'K':
        unit = 'KB'
    elif unit == 'M':
        unit = 'MB'
    elif unit == 'G':
        unit = 'GB'
    elif unit == 'T':
        unit = 'TB'
    elif unit == 'P':
        unit = 'PB'
    elif unit == 'E':
        unit = 'EB'
    
    return int(number * multipliers.get(unit, 1))


def get_file_hash(file_path: str, algorithm: str = "md5") -> Optional[str]:
    """Calculate file hash.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256')
        
    Returns:
        File hash or None if error
    """
    try:
        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except (OSError, IOError, ValueError):
        return None


def is_hidden_file(file_path: str) -> bool:
    """Check if file is hidden.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if file is hidden
    """
    # On Windows, check file attributes
    if sys.platform.startswith('win'):
        try:
            import stat
            attrs = os.stat(file_path).st_file_attributes
            return attrs & stat.FILE_ATTRIBUTE_HIDDEN
        except (AttributeError, OSError):
            pass
    
    # Unix-like systems: hidden if starts with dot
    return os.path.basename(file_path).startswith('.')


def is_binary_file(file_path: str, chunk_size: int = 8192) -> bool:
    """Check if file is binary.
    
    Args:
        file_path: Path to file
        chunk_size: Size of chunk to read for detection
        
    Returns:
        True if file appears to be binary
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            if not chunk:
                return False
            
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return True
            
            # Check for high ratio of non-printable characters
            printable_chars = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in (9, 10, 13))
            ratio = printable_chars / len(chunk)
            return ratio < 0.7
            
    except (OSError, IOError):
        return True  # Assume binary if can't read


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """Sanitize filename for safe filesystem usage.
    
    Args:
        filename: Original filename
        replacement: Character to replace invalid characters with
        
    Returns:
        Sanitized filename
    """
    # Remove/replace invalid characters
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, replacement, filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Handle reserved names on Windows
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    name_part = sanitized.split('.')[0].upper()
    if name_part in reserved_names:
        sanitized = f"{replacement}{sanitized}"
    
    # Ensure not empty
    if not sanitized:
        sanitized = "unnamed"
    
    return sanitized


def ensure_directory_exists(directory_path: str) -> bool:
    """Ensure directory exists, create if necessary.
    
    Args:
        directory_path: Path to directory
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except (OSError, IOError):
        return False


def get_system_info() -> Dict[str, Any]:
    """Get system information.
    
    Returns:
        Dictionary with system information
    """
    import platform
    
    return {
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
    }


def load_json_file(file_path: str, default: Any = None) -> Any:
    """Load JSON file with error handling.
    
    Args:
        file_path: Path to JSON file
        default: Default value if file can't be loaded
        
    Returns:
        Loaded JSON data or default value
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, IOError, json.JSONDecodeError) as e:
        logging.getLogger(__name__).warning("Failed to load JSON file %s: %s", file_path, e)
        return default


def save_json_file(file_path: str, data: Any, indent: int = 2) -> bool:
    """Save data to JSON file.
    
    Args:
        file_path: Path to JSON file
        data: Data to save
        indent: JSON indentation
        
    Returns:
        True if saved successfully
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory:
            ensure_directory_exists(directory)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except (OSError, IOError, TypeError) as e:
        logging.getLogger(__name__).error("Failed to save JSON file %s: %s", file_path, e)
        return False


def validate_file_extension(file_path: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension against allowed list.
    
    Args:
        file_path: Path to file
        allowed_extensions: List of allowed extensions (with or without dots)
        
    Returns:
        True if extension is allowed
    """
    if not allowed_extensions:
        return True
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Normalize extensions (ensure they start with dot)
    normalized_extensions = []
    for ext in allowed_extensions:
        ext = ext.lower()
        if not ext.startswith('.'):
            ext = '.' + ext
        normalized_extensions.append(ext)
    
    return file_ext in normalized_extensions


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    if max_length <= len(suffix):
        return suffix[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def get_relative_path(file_path: str, base_path: str) -> str:
    """Get relative path from base path.
    
    Args:
        file_path: Full file path
        base_path: Base path to make relative to
        
    Returns:
        Relative path or original path if can't make relative
    """
    try:
        return os.path.relpath(file_path, base_path)
    except ValueError:
        # Can't make relative (different drives on Windows, etc.)
        return file_path


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None, 
                 log_format: Optional[str] = None) -> logging.Logger:
    """Setup logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
        log_format: Optional log format string
        
    Returns:
        Configured logger
    """
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[]
    )
    
    logger = logging.getLogger('filepulse')
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        try:
            ensure_directory_exists(os.path.dirname(log_file))
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(logging.Formatter(log_format))
            logger.addHandler(file_handler)
        except (OSError, IOError) as e:
            logger.warning("Failed to setup file logging to %s: %s", log_file, e)
    
    return logger


class PerformanceTimer:
    """Simple performance timer context manager."""
    
    def __init__(self, operation_name: str = "Operation", logger: Optional[logging.Logger] = None):
        """Initialize timer.
        
        Args:
            operation_name: Name of the operation being timed
            logger: Optional logger to log results to
        """
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger(__name__)
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.end_time = time.perf_counter()
        duration = self.end_time - self.start_time
        self.logger.debug(f"{self.operation_name} took {duration:.4f} seconds")
    
    @property
    def duration(self) -> Optional[float]:
        """Get duration in seconds if timer has completed."""
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        return None
