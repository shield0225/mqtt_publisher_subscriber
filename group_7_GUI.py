import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import json
from group_7_SafeLogger import SafeLogger
from group_7_publisher_heartrate import HeartRatePublisher
from group_7_publisher_bloodpressure import BloodPressurePublisher
from group_7_publisher_sp02 import SpO2Publisher

class App:
    def __init__(self, master):
        self.master = master
        master.title("Group 7 - Health Data Publisher Simulator")
        
        self.logger = SafeLogger()

        self.heart_publisher = HeartRatePublisher(lambda msg: self.logger.log(msg, "Heart Rate"), self.logger)
        self.bp_publisher = BloodPressurePublisher(lambda msg: self.logger.log(msg, "Blood Pressure"), self.logger)
        self.spo2_publisher = SpO2Publisher(lambda msg: self.logger.log(msg, "SpO2"), self.logger)

        self.setup_data_displays_and_controls()
        
    def setup_data_displays_and_controls(self):
        """Data displays and corresponding controls"""
        self.setup_topic_frame(0, "Heart Rate", self.heart_publisher)
        self.setup_topic_frame(1, "Blood Pressure", self.bp_publisher)
        self.setup_topic_frame(2, "SpO2", self.spo2_publisher)

    def setup_topic_frame(self, row, label, publisher):
        # Helper function to create a frame for each data topic.
        frame = tk.Frame(self.master, width=400, borderwidth=2, relief="groove", padx=1, pady=5)
        frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
        self.master.columnconfigure(0, weight=1) 
        tk.Label(frame, text=f"{label}:", font=("Arial", 11)).grid(row=0, column=0, sticky="w")
        display_label = tk.Label(frame, text="N/A", font=("Arial", 11))
        display_label.grid(row=0, column=1, sticky="w")

        # Setting up the log area for each publisher
        log_frame = tk.Frame(frame, borderwidth=2, relief="sunken", padx=10, pady=10)
        log_frame.grid(row=2, column=0, columnspan=4, rowspan=4, padx=10, pady=10, sticky='ew')
        log_text = ScrolledText(log_frame, height=8, width=100)
        log_text.pack(fill=tk.BOTH, expand=True)
        self.logger.register_log_widget(label, log_text)

        if label == "Heart Rate":
            self.heart_rate_value = display_label
        elif label == "Blood Pressure":
            self.blood_pressure_value = display_label
        elif label == "SpO2":
            self.spo2_value = display_label

        # Control buttons within the same frame
        button_width = 20
        tk.Button(frame, text=f"Start", command=publisher.start, width=button_width).grid(row=2, column=8, padx=3, pady=3)
        tk.Button(frame, text=f"Stop", command=publisher.stop, width=button_width).grid(row=3, column=8, padx=3, pady=3)
        tk.Button(frame, text=f"Send Wild Data", command=lambda: self.send_wild_data(publisher), width=button_width).grid(row=4, column=8, padx=3, pady=3)
        tk.Button(frame, text=f"Miss Transmission", command=lambda: self.miss_transmission(publisher), width=button_width).grid(row=5, column=8, padx=3, pady=3)

    def handle_data(self, data):
        """Process JSON data received from publishers and update GUI."""
        try:
            data = json.loads(data)
            if 'heart_rate' in data:
                self.master.after(0, lambda: self.heart_rate_value.config(text=f"{data['heart_rate']} bpm"))
            if 'blood_pressure' in data:
                bp = data['blood_pressure']
                self.master.after(0, lambda: self.blood_pressure_value.config(text=f"{bp[0]}/{bp[1]} mmHg"))
            if 'spO2' in data:
                self.master.after(0, lambda: self.spo2_value.config(text=f"{data['spO2']}%"))
        except json.JSONDecodeError:
            self.log_message("Error decoding JSON data from publisher.")
        except Exception as e:
            self.log_message(f"Error processing data: {str(e)}")
  
    def update_data_display(self, data):
        """Update the GUI with new data."""
        if "heart_rate" in data:
            self.heart_rate_value.config(text=f"{data['heart_rate']} bpm")
        if "blood_pressure" in data:
            self.blood_pressure_value.config(text=f"{data['blood_pressure'][0]}/{data['blood_pressure'][1]} mmHg")
        if "spO2" in data:
            self.spo2_value.config(text=f"{data['spO2']}%")

    def send_wild_data(self, publisher, label):
        # Implement functionality
        self.logger.log(f"Sending wild data for {label}", label)

    def miss_transmission(self, publisher, label):
        # Implement functionality
        self.logger.log(f"Missed transmission for {label}", label)


    def setup_log_display(self):
        """Setup the log display area and assign it to self.logger."""
        log_frame = tk.Frame(self.master, borderwidth=2, relief="sunken", padx=10, pady=10)
        log_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
        log_text = ScrolledText(log_frame, height=10, width=50)
        log_text.pack(fill=tk.BOTH, expand=True)
        return log_text  # This should be assigned to self.logger

    def log_message(self, message, label):
        """Log a message to the ScrolledText widget."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.logger.log(message, label)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.geometry("1100x600")
    root.mainloop()
