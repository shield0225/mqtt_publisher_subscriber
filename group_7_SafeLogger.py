import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

class SafeLogger:
    def __init__(self):
        self.log_widgets = {}

    def register_log_widget(self, label, widget):
        """Register a text widget for logging with a specific label."""
        self.log_widgets[label] = widget
        print(f"Registered log widget for label: {label}")

    def log(self, message, label):
        print(f"Attempting to log: {message} under {label}")
        """Log a message to the registered text widget with the specified label."""
        if label in self.log_widgets:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            def append_message():
                self.log_widgets[label].insert(tk.END, formatted_message)
                self.log_widgets[label].see(tk.END)
            self.log_widgets[label].after(0, append_message)
        else:
            print(f"Log label '{label}' not registered. Available labels: {self.log_widgets.keys()}")

