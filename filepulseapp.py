#!/usr/bin/env python3
"""
FilePulse - Clean Launcher
Simple, fast startup without splash screen animations.
"""
import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path


class FilePulseLauncher:
    """Clean FilePulse launcher without splash screen."""
    
    def __init__(self):
        self.setup_paths()
        
    def setup_paths(self):
        """Add FilePulse module to Python path."""
        current_dir = Path(__file__).parent.resolve()
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
            
        # Verify FilePulse module exists
        filepulse_path = current_dir / "filepulse"
        if not filepulse_path.exists():
            raise ImportError(f"FilePulse module not found at: {filepulse_path}")
    
    def launch(self):
        """Launch FilePulse GUI directly."""
        try:
            # Import FilePulse components
            from filepulse.gui import FilePulseGUI
            from filepulse.config import Config
            
            # Create main window
            root = tk.Tk()
            root.title("FilePulse - Filesystem Monitor")
            root.geometry("900x700")
            root.minsize(800, 600)
            
            # Set window icon if available
            try:
                icon_path = Path(__file__).parent / "assets" / "icon.ico"
                if icon_path.exists():
                    root.iconbitmap(str(icon_path))
            except:
                pass  # Ignore icon errors
            
            # Load configuration
            config = Config()
            
            # Apply clean styling
            self.apply_clean_theme(root)
            
            # Create and start application (no splash screen)
            app = FilePulseGUI(config, show_splash=False, root=root)
            
            # Start GUI main loop
            root.mainloop()
            
        except ImportError as e:
            self.show_error("Import Error", 
                           f"Failed to import FilePulse:\n\n{e}\n\n"
                           f"Please ensure FilePulse is properly installed.")
        except Exception as e:
            self.show_error("Startup Error", 
                           f"Failed to start FilePulse:\n\n{e}")
    
    def apply_clean_theme(self, root):
        """Apply clean, professional theme."""
        # Configure ttk styles for a cleaner look
        style = ttk.Style()
        
        # Use a clean theme
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # Custom colors for clean appearance
        style.configure('Heading.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Clean.TButton', padding=6)
        style.configure('Status.TLabel', foreground='#666666')
    
    def show_error(self, title, message):
        """Show error dialog."""
        try:
            import tkinter.messagebox as msgbox
            root = tk.Tk()
            root.withdraw()  # Hide root window
            msgbox.showerror(title, message)
            root.destroy()
        except:
            print(f"Error: {title} - {message}")  # Fallback to console


def main():
    """Main entry point."""
    try:
        launcher = FilePulseLauncher()
        launcher.launch()
    except Exception as e:
        print(f"Fatal error: {e}")


if __name__ == "__main__":
    main()
