import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

class SafeLogger:
    def __init__(self):
        self.log_widgets = {}

    def register_log_widget(self, label, widget):
        """Register a text widget for logging with a specific label."""
        self.log_widgets[label] = widget

    def log(self, message, label):
        """Log a message to the registered text widget with the specified label."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        def append_message():
            """Append the formatted message to the text widget."""
            if label in self.log_widgets:
                self.log_widgets[label].insert(tk.END, formatted_message)
                self.log_widgets[label].see(tk.END)

        # Use tkinter's after method to schedule updates to be run in the main thread
        if label in self.log_widgets:
            self.log_widgets[label].after(0, append_message)
        else:
            print(f"Log label '{label}' not registered.")

