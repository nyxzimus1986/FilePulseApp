"""
Advanced splash screen functionality for FilePulseApp.

This module extends the basic splash screen with additional features and customization options.
"""

import tkinter as tk
from tkinter import ttk
import json
import os
from typing import Optional, Dict, Any
import time
import threading

from .splash import SplashScreen
from .utils import load_json_file


class AdvancedSplashScreen(SplashScreen):
    """Advanced splash screen with preset support and enhanced features."""
    
    def __init__(self, parent: tk.Tk, preset_path: Optional[str] = None, 
                 preset_name: Optional[str] = None, duration: int = None):
        """Initialize advanced splash screen.
        
        Args:
            parent: Parent tkinter window
            preset_path: Path to preset file
            preset_name: Name of built-in preset to use
            duration: Override duration from preset
        """
        self.preset_config = self._load_preset(preset_path, preset_name)
        
        # Get duration from preset or use provided value
        if duration is None:
            duration = self.preset_config.get('settings', {}).get('duration', 3000)
        
        # Initialize parent class
        super().__init__(parent, duration)
    
    def _load_preset(self, preset_path: Optional[str], preset_name: Optional[str]) -> Dict[str, Any]:
        """Load splash screen preset configuration.
        
        Args:
            preset_path: Path to custom preset file
            preset_name: Name of built-in preset
            
        Returns:
            Preset configuration dictionary
        """
        if preset_path and os.path.exists(preset_path):
            config = load_json_file(preset_path, {})
            if config:
                return config
        
        # Load built-in preset
        if preset_name:
            assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'presets')
            preset_file = f"splash-preset-{preset_name}.json"
            preset_path = os.path.join(assets_dir, preset_file)
            
            if os.path.exists(preset_path):
                config = load_json_file(preset_path, {})
                if config:
                    return config
        
        # Default configuration
        return {
            "settings": {
                "title": "FilePulseApp",
                "subtitle": "File Monitoring System",
                "duration": 3000,
                "background_color": "#2c3e50",
                "text_color": "#ecf0f1",
                "accent_color": "#3498db"
            }
        }
    
    def setup_content(self):
        """Setup advanced splash screen content based on preset."""
        settings = self.preset_config.get('settings', {})
        content = self.preset_config.get('content', {})
        styling = self.preset_config.get('styling', {})
        
        # Get colors
        bg_color = settings.get('background_color', '#2c3e50')
        text_color = settings.get('text_color', '#ecf0f1')
        accent_color = settings.get('accent_color', '#3498db')
        title_color = settings.get('title_color', accent_color)
        subtitle_color = settings.get('subtitle_color', text_color)
        
        # Main frame
        main_frame = tk.Frame(self.splash, bg=bg_color, padx=30, pady=30)
        main_frame.pack(fill='both', expand=True)
        
        # Title section
        title_text = settings.get('title', 'FilePulseApp')
        title_font = styling.get('title_font', ['Helvetica', 24, 'bold'])
        
        title_label = tk.Label(
            main_frame,
            text=title_text,
            font=title_font,
            fg=title_color,
            bg=bg_color
        )
        title_label.pack(pady=(10, 5))
        
        # Subtitle
        if settings.get('subtitle'):
            subtitle_font = styling.get('subtitle_font', ['Helvetica', 12])
            subtitle_label = tk.Label(
                main_frame,
                text=settings['subtitle'],
                font=subtitle_font,
                fg=subtitle_color,
                bg=bg_color
            )
            subtitle_label.pack(pady=(0, 20))
        
        # Logo section
        if settings.get('show_logo', True):
            self.create_logo_section(main_frame, bg_color, accent_color)
        
        # Features section
        if settings.get('show_features', False):
            features = content.get('features', [])
            if features:
                self.create_features_section(main_frame, features, text_color, bg_color, styling)
        
        # Progress section
        if settings.get('show_progress', True):
            self.create_progress_section(main_frame, bg_color, accent_color)
        
        # Version info
        if settings.get('show_version', True):
            version_font = styling.get('version_font', ['Helvetica', 8])
            version_label = tk.Label(
                main_frame,
                text="Version 1.0.0",
                font=version_font,
                fg=text_color,
                bg=bg_color
            )
            version_label.pack(side='bottom', pady=(10, 0))
        
        # Start animations
        loading_messages = content.get('loading_messages', ["Loading..."])
        self.animate_status_with_messages(loading_messages)
    
    def create_logo_section(self, parent, bg_color, accent_color):
        """Create logo section."""
        logo_frame = tk.Frame(parent, bg=bg_color)
        logo_frame.pack(pady=15)
        
        # Create canvas for custom logo
        canvas = tk.Canvas(logo_frame, width=100, height=100, bg=bg_color, highlightthickness=0)
        canvas.pack()
        
        # Draw a modern file monitoring icon
        self.draw_monitoring_icon(canvas, accent_color)
    
    def draw_monitoring_icon(self, canvas, color):
        """Draw a monitoring icon on canvas."""
        # Central circle (represents monitoring hub)
        canvas.create_oval(35, 35, 65, 65, outline=color, width=3, fill='')
        
        # Inner pulse circle
        canvas.create_oval(42, 42, 58, 58, outline=color, width=2, fill=color)
        
        # Monitoring rays
        import math
        for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            x1 = 50 + 20 * math.cos(math.radians(angle))
            y1 = 50 + 20 * math.sin(math.radians(angle))
            x2 = 50 + 28 * math.cos(math.radians(angle))
            y2 = 50 + 28 * math.sin(math.radians(angle))
            canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
        
        # File icons around the monitoring hub
        file_positions = [(25, 15), (75, 15), (85, 50), (75, 85), (25, 85), (15, 50)]
        for i, (x, y) in enumerate(file_positions):
            if i % 2 == 0:  # Draw every other file icon
                canvas.create_rectangle(x-3, y-3, x+3, y+3, outline=color, fill='')
    
    def create_features_section(self, parent, features, text_color, bg_color, styling):
        """Create features section."""
        features_frame = tk.Frame(parent, bg=bg_color)
        features_frame.pack(pady=15)
        
        feature_font = styling.get('feature_font', ['Helvetica', 9])
        
        for feature in features:
            feature_label = tk.Label(
                features_frame,
                text=feature,
                font=feature_font,
                fg=text_color,
                bg=bg_color,
                anchor='w'
            )
            feature_label.pack(fill='x', pady=1)
    
    def create_progress_section(self, parent, bg_color, accent_color):
        """Create progress section."""
        progress_frame = tk.Frame(parent, bg=bg_color)
        progress_frame.pack(fill='x', pady=(20, 0))
        
        # Custom styled progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            background=accent_color,
            troughcolor=bg_color,
            borderwidth=1,
            lightcolor=accent_color,
            darkcolor=accent_color
        )
        
        self.progress = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=250,
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=(0, 10))
        self.progress.start(8)
        
        # Status label
        self.status_label = tk.Label(
            progress_frame,
            text="Initializing...",
            font=('Helvetica', 9),
            fg=self.preset_config.get('settings', {}).get('text_color', '#ecf0f1'),
            bg=bg_color
        )
        self.status_label.pack()
    
    def animate_status_with_messages(self, messages):
        """Animate status with custom messages."""
        if not hasattr(self, 'status_label') or not messages:
            return
        
        self.message_index = 0
        self.messages = messages
        self.animate_next_message()
    
    def animate_next_message(self):
        """Animate to next message."""
        if not hasattr(self, 'status_label') or not self.splash.winfo_exists():
            return
        
        if self.messages:
            message = self.messages[self.message_index]
            self.status_label.config(text=message)
            self.message_index = (self.message_index + 1) % len(self.messages)
        
        # Schedule next update
        self.splash.after(600, self.animate_next_message)


def create_advanced_splash(parent: tk.Tk, preset_name: str = "default", 
                          duration: Optional[int] = None) -> AdvancedSplashScreen:
    """Create advanced splash screen with preset.
    
    Args:
        parent: Parent tkinter window
        preset_name: Name of preset to use ("default", "professional-dark")
        duration: Override duration in milliseconds
        
    Returns:
        AdvancedSplashScreen instance
    """
    return AdvancedSplashScreen(parent, preset_name=preset_name, duration=duration)
