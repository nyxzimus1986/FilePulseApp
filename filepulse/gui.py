"""
Graphical User Interface for FilePulseApp.

This module provides the main GUI interface using tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import time
from typing import Optional, List
import logging

from .monitor import FileMonitor, FileEvent
from .config import Config
from .output import OutputManager
from .splash import SplashScreen


class FileEventListFrame(ttk.Frame):
    """Frame for displaying file events in a list."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_widgets()
        self.events = []
    
    def setup_widgets(self):
        """Setup the widgets for the event list."""
        # Create treeview for events
        columns = ("Time", "Event", "File")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("Time", text="Time")
        self.tree.heading("Event", text="Event")
        self.tree.heading("File", text="File Path")
        
        self.tree.column("Time", width=150, minwidth=120)
        self.tree.column("Event", width=100, minwidth=80)
        self.tree.column("File", width=400, minwidth=200)
        
        # Configure tags for different source types
        self.tree.tag_configure("system", foreground="#666666", background="#f5f5f5")
        self.tree.tag_configure("user", foreground="#000000", background="#ffffff")
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy Path", command=self.copy_path)
        self.context_menu.add_command(label="Open File", command=self.open_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Clear All", command=self.clear_events)
        
        self.tree.bind("<Button-3>", self.show_context_menu)  # Right click
    
    def add_event(self, event: FileEvent):
        """Add a file event to the list."""
        timestamp = time.strftime("%H:%M:%S", time.localtime(event.timestamp))
        
        # Insert at the top of the list
        item_id = self.tree.insert("", 0, values=(timestamp, event.event_type.title(), event.file_path))
        
        # Color code based on event type and source
        event_icon = ""
        if event.event_type == "created":
            event_icon = "📄 Created"
        elif event.event_type == "modified":
            event_icon = "✏️ Modified"
        elif event.event_type == "deleted":
            event_icon = "🗑️ Deleted"
        elif event.event_type == "moved":
            event_icon = "📁 Moved"
        
        # Add source indicator
        source_icon = "🔧" if event.is_system_change() else "👤"
        event_display = f"{source_icon} {event_icon}"
        
        self.tree.set(item_id, "Event", event_display)
        
        # Apply different colors based on source type
        if event.is_system_change():
            self.tree.set(item_id, tags=("system",))
        else:
            self.tree.set(item_id, tags=("user",))
        
        self.events.insert(0, event)
        
        # Limit the number of displayed events
        if len(self.events) > 1000:
            # Remove oldest events
            items = self.tree.get_children()
            for item in items[1000:]:
                self.tree.delete(item)
            self.events = self.events[:1000]
    
    def clear_events(self):
        """Clear all events from the list."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.events.clear()
    
    def show_context_menu(self, event):
        """Show context menu on right click."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def copy_path(self):
        """Copy selected file path to clipboard."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            file_path = self.tree.item(item)["values"][2]
            self.clipboard_clear()
            self.clipboard_append(file_path)
    
    def open_file(self):
        """Open selected file with default application."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            file_path = self.tree.item(item)["values"][2]
            try:
                import os
                import subprocess, sys
                if sys.platform.startswith('win'):
                    os.startfile(file_path)
                elif sys.platform.startswith('darwin'):
                    subprocess.call(['open', file_path])
                else:
                    subprocess.call(['xdg-open', file_path])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")


class ControlPanel(ttk.Frame):
    """Control panel for monitoring operations."""
    
    def __init__(self, parent, on_start_callback, on_stop_callback, on_add_path_callback, on_filter_change_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_start_callback = on_start_callback
        self.on_stop_callback = on_stop_callback
        self.on_add_path_callback = on_add_path_callback
        self.on_filter_change_callback = on_filter_change_callback
        self.is_monitoring = False
        
        # Filter variables
        self.show_system_var = tk.BooleanVar(value=True)
        self.show_user_var = tk.BooleanVar(value=True)
        self.separate_changes_var = tk.BooleanVar(value=True)
        
        self.setup_widgets()
    
    def setup_widgets(self):
        """Setup control panel widgets."""
        # Monitoring controls
        control_frame = ttk.LabelFrame(self, text="Monitoring Controls")
        control_frame.pack(fill="x", padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Monitoring", 
                                      command=self.toggle_monitoring)
        self.start_button.pack(side="left", padx=5, pady=5)
        
        self.status_label = ttk.Label(control_frame, text="Status: Stopped", 
                                     foreground="red")
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Filtering controls
        filter_frame = ttk.LabelFrame(self, text="Event Filtering")
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Checkbutton(filter_frame, text="👤 Show User Changes",
                       variable=self.show_user_var,
                       command=self.on_filter_changed).pack(anchor="w", padx=5, pady=2)
        
        ttk.Checkbutton(filter_frame, text="🔧 Show System Changes",
                       variable=self.show_system_var,
                       command=self.on_filter_changed).pack(anchor="w", padx=5, pady=2)
        
        ttk.Checkbutton(filter_frame, text="Separate System/User Changes",
                       variable=self.separate_changes_var,
                       command=self.on_filter_changed).pack(anchor="w", padx=5, pady=2)
        
        # Statistics display
        self.stats_label = ttk.Label(filter_frame, text="Events: Total: 0, User: 0, System: 0")
        self.stats_label.pack(anchor="w", padx=5, pady=2)
        
        # Path management
        path_frame = ttk.LabelFrame(self, text="Watch Directories")
        path_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Path list
        self.path_listbox = tk.Listbox(path_frame, height=4)
        self.path_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Path buttons
        button_frame = ttk.Frame(path_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Add Directory", 
                  command=self.add_directory).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Remove Selected", 
                  command=self.remove_directory).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_directories).pack(side="left", padx=2)
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off."""
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start monitoring."""
        if self.on_start_callback():
            self.is_monitoring = True
            self.start_button.config(text="Stop Monitoring")
            self.status_label.config(text="Status: Running", foreground="green")
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.on_stop_callback()
        self.is_monitoring = False
        self.start_button.config(text="Start Monitoring")
        self.status_label.config(text="Status: Stopped", foreground="red")
    
    def add_directory(self):
        """Add directory to watch list."""
        directory = filedialog.askdirectory(title="Select Directory to Monitor")
        if directory:
            self.path_listbox.insert(tk.END, directory)
            self.on_add_path_callback(directory)
    
    def remove_directory(self):
        """Remove selected directory from watch list."""
        selection = self.path_listbox.curselection()
        if selection:
            self.path_listbox.delete(selection[0])
    
    def clear_directories(self):
        """Clear all directories from watch list."""
        self.path_listbox.delete(0, tk.END)
    
    def on_filter_changed(self):
        """Handle filter option changes."""
        if self.on_filter_change_callback:
            self.on_filter_change_callback(
                show_system=self.show_system_var.get(),
                show_user=self.show_user_var.get(),
                separate=self.separate_changes_var.get()
            )
    
    def update_stats(self, stats: dict):
        """Update statistics display.
        
        Args:
            stats: Dictionary containing event statistics
        """
        total = stats.get('total_events', 0)
        user = stats.get('user_events', 0)
        system = stats.get('system_events', 0)
        self.stats_label.config(text=f"Events: Total: {total}, User: {user}, System: {system}")
    
    def load_directories(self, directories: List[str]):
        """Load directories into the list."""
        self.clear_directories()
        for directory in directories:
            self.path_listbox.insert(tk.END, directory)


class FilePulseGUI:
    """Main GUI application class."""
    
    def __init__(self, config: Config = None, show_splash: bool = True, root: tk.Tk = None):
        """Initialize the GUI application.
        
        Args:
            config: Configuration object (will create default if None)
            show_splash: Whether to show splash screen
            root: Root window (will create if None)
        """
        self.config = config or Config()
        self.monitor = None
        self.output_manager = OutputManager(self.config)
        self.event_queue = queue.Queue()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize main window
        if root is not None:
            self.root = root
            self.root.title("FilePulse - Filesystem Monitor")
            # Don't show splash screen when root is provided
            show_splash = False
        else:
            self.root = tk.Tk()
            self.root.title("FilePulseApp - File Monitoring System")
            self.root.geometry("900x700")
        
        # Show splash screen if enabled
        if show_splash and self.config.get("gui", "splash_enabled"):
            splash = SplashScreen(self.root)
            splash_duration = self.config.get("gui", "splash_duration") or 3000
            self.root.after(splash_duration, splash.destroy)
        
        self.setup_gui()
        self.setup_monitoring()
        
        # Start event processing
        self.process_events()
    
    def setup_gui(self):
        """Setup the main GUI components."""
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        self.control_panel = ControlPanel(
            left_frame,
            on_start_callback=self.start_monitoring,
            on_stop_callback=self.stop_monitoring,
            on_add_path_callback=self.add_watch_path,
            on_filter_change_callback=self.on_filter_changed
        )
        self.control_panel.pack(fill="both", expand=True)
        
        # Load existing directories
        self.control_panel.load_directories(self.config.get_watch_directories())
        
        # Right panel - Event list
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=3)
        
        ttk.Label(right_frame, text="File Events", font=("TkDefaultFont", 12, "bold")).pack(pady=5)
        
        self.event_list = FileEventListFrame(right_frame)
        self.event_list.pack(fill="both", expand=True)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief="sunken")
        self.status_bar.pack(side="bottom", fill="x")
        
        # Menu bar
        self.setup_menu()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_menu(self):
        """Setup the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Events...", command=self.export_events)
        file_menu.add_separator()
        file_menu.add_command(label="Settings...", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Clear Events", command=self.clear_events)
        view_menu.add_command(label="Refresh", command=self.refresh_display)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_monitoring(self):
        """Setup file monitoring."""
        monitor_config = self.config.get("monitoring")
        self.monitor = FileMonitor(
            callback=self.file_event_callback, 
            config=monitor_config,
            full_config=self.config.config
        )
        
        # Add configured watch directories
        for directory in self.config.get_watch_directories():
            self.monitor.add_watch_path(directory)
    
    def file_event_callback(self, event: FileEvent):
        """Callback for file events (runs in monitoring thread)."""
        # Add event to queue for processing in main thread
        self.event_queue.put(event)
    
    def process_events(self):
        """Process events from the queue (runs in main thread)."""
        try:
            while True:
                event = self.event_queue.get_nowait()
                self.event_list.add_event(event)
                self.output_manager.log_event(event)
                
                # Update status bar
                self.status_bar.config(text=f"Last event: {event.event_type} - {event.file_path}")
        except queue.Empty:
            pass
        
        # Update statistics periodically
        if hasattr(self, 'monitor') and self.monitor:
            stats = self.monitor.get_stats()
            self.control_panel.update_stats(stats)
        
        # Schedule next check
        self.root.after(100, self.process_events)
    
    def on_filter_changed(self, show_system: bool, show_user: bool, separate: bool):
        """Handle filter option changes.
        
        Args:
            show_system: Whether to show system-generated changes
            show_user: Whether to show user-generated changes
            separate: Whether to enable system/user separation
        """
        if hasattr(self, 'monitor') and self.monitor:
            self.monitor.set_filtering_options(show_system, show_user, separate)
            self.logger.info(f"Filter options updated: system={show_system}, user={show_user}, separate={separate}")
    
    def start_monitoring(self) -> bool:
        """Start file monitoring.
        
        Returns:
            True if monitoring started successfully
        """
        if not self.monitor:
            return False
        
        if self.monitor.start_monitoring():
            self.status_bar.config(text="Monitoring started")
            self.logger.info("File monitoring started")
            return True
        else:
            messagebox.showerror("Error", "Failed to start file monitoring")
            return False
    
    def stop_monitoring(self):
        """Stop file monitoring."""
        if self.monitor:
            self.monitor.stop_monitoring()
            self.status_bar.config(text="Monitoring stopped")
            self.logger.info("File monitoring stopped")
    
    def add_watch_path(self, path: str):
        """Add a path to monitor."""
        if self.monitor:
            if self.monitor.add_watch_path(path):
                self.config.add_watch_directory(path)
                self.status_bar.config(text=f"Added watch path: {path}")
    
    def clear_events(self):
        """Clear all events from display."""
        self.event_list.clear_events()
        self.status_bar.config(text="Events cleared")
    
    def refresh_display(self):
        """Refresh the display."""
        self.status_bar.config(text="Display refreshed")
    
    def export_events(self):
        """Export events to file."""
        file_path = filedialog.asksaveasfilename(
            title="Export Events",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Determine format from extension
            extension = file_path.lower().split('.')[-1]
            format_type = "json" if extension == "json" else "csv" if extension == "csv" else "txt"
            
            if self.output_manager.export_events(file_path, format_type):
                messagebox.showinfo("Success", f"Events exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export events")
    
    def show_settings(self):
        """Show settings dialog."""
        messagebox.showinfo("Settings", "Settings dialog not implemented yet.")
    
    def show_about(self):
        """Show about dialog."""
        about_text = """FilePulseApp v1.0.0

A file monitoring and pulse detection system.

Features:
- Real-time file system monitoring
- Multiple output formats
- Configurable monitoring options
- Cross-platform support

© 2025 FilePulse Development Team"""
        
        messagebox.showinfo("About FilePulseApp", about_text)
    
    def on_closing(self):
        """Handle application closing."""
        if self.monitor and self.monitor.is_monitoring:
            self.stop_monitoring()
        
        self.output_manager.close()
        self.config.save_config()
        self.root.destroy()
    
    def run(self):
        """Run the GUI application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
