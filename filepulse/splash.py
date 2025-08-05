"""
Splash screen functionality for FilePulseApp.

This module provides splash screen capabilities for the application startup.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional
import os


class SplashScreen:
    """Simple splash screen for application startup."""
    
    def __init__(self, parent: tk.Tk, duration: int = 3000):
        """Initialize splash screen.
        
        Args:
            parent: Parent tkinter window
            duration: Duration to show splash screen in milliseconds
        """
        self.parent = parent
        self.duration = duration
        
        # Create splash window
        self.splash = tk.Toplevel(parent)
        self.splash.title("FilePulseApp")
        self.splash.geometry("400x300")
        self.splash.resizable(False, False)
        
        # Center the splash screen
        self.center_window()
        
        # Remove window decorations
        self.splash.overrideredirect(True)
        
        # Setup splash content
        self.setup_content()
        
        # Make splash stay on top
        self.splash.lift()
        self.splash.attributes('-topmost', True)
        
        # Hide main window during splash
        self.parent.withdraw()
        
        # Auto-close after duration
        if duration > 0:
            self.splash.after(duration, self.destroy)
    
    def center_window(self):
        """Center the splash window on screen."""
        self.splash.update_idletasks()
        width = self.splash.winfo_width()
        height = self.splash.winfo_height()
        x = (self.splash.winfo_screenwidth() // 2) - (width // 2)
        y = (self.splash.winfo_screenheight() // 2) - (height // 2)
        self.splash.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_content(self):
        """Setup splash screen content."""
        # Main frame
        main_frame = tk.Frame(self.splash, bg='#2c3e50', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="FilePulseApp",
            font=("Arial", 24, "bold"),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        title_label.pack(pady=(20, 10))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="File Monitoring & Pulse Detection System",
            font=("Arial", 12),
            fg='#bdc3c7',
            bg='#2c3e50'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Logo placeholder (would be replaced with actual logo)
        logo_frame = tk.Frame(main_frame, bg='#34495e', width=100, height=100)
        logo_frame.pack(pady=20)
        logo_frame.pack_propagate(False)
        
        logo_label = tk.Label(
            logo_frame,
            text="📁\n👁️",
            font=("Arial", 20),
            fg='#3498db',
            bg='#34495e'
        )
        logo_label.pack(expand=True)
        
        # Version info
        version_label = tk.Label(
            main_frame,
            text="Version 1.0.0",
            font=("Arial", 10),
            fg='#95a5a6',
            bg='#2c3e50'
        )
        version_label.pack(pady=(20, 0))
        
        # Loading indicator
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(pady=20)
        self.progress.start(10)
        
        # Loading text
        self.loading_label = tk.Label(
            main_frame,
            text="Loading...",
            font=("Arial", 10),
            fg='#95a5a6',
            bg='#2c3e50'
        )
        self.loading_label.pack()
        
        # Start loading animation
        self.animate_loading()
    
    def animate_loading(self):
        """Animate loading text."""
        loading_texts = ["Loading.", "Loading..", "Loading...", "Loading"]
        current_text = self.loading_label.cget("text")
        
        try:
            current_index = loading_texts.index(current_text)
            next_index = (current_index + 1) % len(loading_texts)
        except ValueError:
            next_index = 0
        
        self.loading_label.config(text=loading_texts[next_index])
        
        # Continue animation if splash is still showing
        if self.splash.winfo_exists():
            self.splash.after(500, self.animate_loading)
    
    def destroy(self):
        """Destroy splash screen and show main window."""
        if self.splash.winfo_exists():
            self.splash.destroy()
        self.parent.deiconify()  # Show main window


class AdvancedSplashScreen(SplashScreen):
    """Advanced splash screen with more features."""
    
    def __init__(self, parent: tk.Tk, duration: int = 3000, image_path: Optional[str] = None):
        """Initialize advanced splash screen.
        
        Args:
            parent: Parent tkinter window
            duration: Duration to show splash screen in milliseconds
            image_path: Path to splash image
        """
        self.image_path = image_path
        super().__init__(parent, duration)
    
    def setup_content(self):
        """Setup advanced splash screen content."""
        # Main frame with gradient-like background
        main_frame = tk.Frame(self.splash, bg='#1a252f', padx=30, pady=30)
        main_frame.pack(fill='both', expand=True)
        
        # Header section
        header_frame = tk.Frame(main_frame, bg='#1a252f')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title with gradient effect simulation
        title_label = tk.Label(
            header_frame,
            text="FilePulseApp",
            font=("Helvetica", 28, "bold"),
            fg='#00d4ff',
            bg='#1a252f'
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Advanced File System Monitoring",
            font=("Helvetica", 14, "italic"),
            fg='#7fb3d3',
            bg='#1a252f'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Image section
        image_frame = tk.Frame(main_frame, bg='#1a252f')
        image_frame.pack(pady=20)
        
        if self.image_path and os.path.exists(self.image_path):
            try:
                from PIL import Image, ImageTk
                image = Image.open(self.image_path)
                image = image.resize((120, 120), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(image)
                
                image_label = tk.Label(
                    image_frame,
                    image=self.photo,
                    bg='#1a252f'
                )
                image_label.pack()
            except ImportError:
                # Fallback if PIL is not available
                self.create_fallback_logo(image_frame)
        else:
            self.create_fallback_logo(image_frame)
        
        # Features section
        features_frame = tk.Frame(main_frame, bg='#1a252f')
        features_frame.pack(pady=20)
        
        features = [
            "🔍 Real-time file monitoring",
            "📊 Event logging & analytics",
            "⚙️ Configurable monitoring rules",
            "🎨 Modern user interface"
        ]
        
        for feature in features:
            feature_label = tk.Label(
                features_frame,
                text=feature,
                font=("Helvetica", 10),
                fg='#c7d2fe',
                bg='#1a252f',
                anchor='w'
            )
            feature_label.pack(fill='x', pady=2)
        
        # Progress section
        progress_frame = tk.Frame(main_frame, bg='#1a252f')
        progress_frame.pack(fill='x', pady=(30, 0))
        
        # Custom styled progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Splash.Horizontal.TProgressbar",
            background='#00d4ff',
            troughcolor='#2d3748',
            borderwidth=0,
            lightcolor='#00d4ff',
            darkcolor='#00d4ff'
        )
        
        self.progress = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=300,
            style="Splash.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=(0, 10))
        self.progress.start(8)
        
        # Status text
        self.status_label = tk.Label(
            progress_frame,
            text="Initializing application...",
            font=("Helvetica", 9),
            fg='#a0aec0',
            bg='#1a252f'
        )
        self.status_label.pack()
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg='#1a252f')
        footer_frame.pack(side='bottom', fill='x', pady=(20, 0))
        
        copyright_label = tk.Label(
            footer_frame,
            text="© 2025 FilePulse Development Team",
            font=("Helvetica", 8),
            fg='#718096',
            bg='#1a252f'
        )
        copyright_label.pack()
        
        # Start status animation
        self.animate_status()
    
    def create_fallback_logo(self, parent):
        """Create a fallback logo when image is not available."""
        logo_frame = tk.Frame(parent, bg='#2d3748', width=120, height=120)
        logo_frame.pack()
        logo_frame.pack_propagate(False)
        
        # Create a simple geometric logo
        canvas = tk.Canvas(logo_frame, width=120, height=120, bg='#2d3748', highlightthickness=0)
        canvas.pack(expand=True)
        
        # Draw circles and lines to represent file monitoring
        canvas.create_oval(30, 30, 90, 90, outline='#00d4ff', width=3, fill='#1a252f')
        canvas.create_oval(45, 45, 75, 75, outline='#7fb3d3', width=2, fill='#00d4ff')
        
        # Draw monitoring "rays"
        for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            import math
            x1 = 60 + 25 * math.cos(math.radians(angle))
            y1 = 60 + 25 * math.sin(math.radians(angle))
            x2 = 60 + 35 * math.cos(math.radians(angle))
            y2 = 60 + 35 * math.sin(math.radians(angle))
            canvas.create_line(x1, y1, x2, y2, fill='#00d4ff', width=2)
    
    def animate_status(self):
        """Animate status text."""
        status_texts = [
            "Initializing application...",
            "Loading configuration...",
            "Setting up monitoring...",
            "Preparing interface...",
            "Almost ready..."
        ]
        
        # Get current text and find next one
        current_text = self.status_label.cget("text")
        try:
            current_index = status_texts.index(current_text)
            next_index = (current_index + 1) % len(status_texts)
        except ValueError:
            next_index = 0
        
        self.status_label.config(text=status_texts[next_index])
        
        # Continue animation if splash is still showing
        if self.splash.winfo_exists():
            self.splash.after(600, self.animate_status)


def show_splash(parent: tk.Tk, duration: int = 3000, advanced: bool = False, 
                image_path: Optional[str] = None) -> SplashScreen:
    """Show splash screen.
    
    Args:
        parent: Parent tkinter window
        duration: Duration in milliseconds
        advanced: Whether to use advanced splash screen
        image_path: Path to splash image (for advanced splash)
        
    Returns:
        SplashScreen instance
    """
    if advanced:
        return AdvancedSplashScreen(parent, duration, image_path)
    else:
        return SplashScreen(parent, duration)
