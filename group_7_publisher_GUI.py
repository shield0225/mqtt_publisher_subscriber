import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import json
import publishers.group_7_basepublisher as basepublisher
from Utils.group_7_SafeLogger import SafeLogger
from publishers.group_7_publisher_heartrate import HeartRatePublisher
from publishers.group_7_publisher_bloodpressure import BloodPressurePublisher
from publishers.group_7_publisher_sp02 import SpO2Publisher
import Utils.group_7_config as config
from functools import partial

class App:
    def __init__(self, master):
        self.master = master
        master.title("Group 7 - Health Data Publisher Simulator")
        
        self.logger = SafeLogger()
        print(f"Logger initialized in App: {self.logger}")

        heart_rate_topic = "health/heart_rate"
        blood_pressure_topic = "health/blood_pressure"
        spo2_topic = "health/spo2"

        self.heart_publisher = HeartRatePublisher(lambda msg: self.logger.log(msg, "Heart Rate"), self.logger, heart_rate_topic)
        self.bp_publisher = BloodPressurePublisher(lambda msg: self.logger.log(msg, "Blood Pressure"), self.logger, blood_pressure_topic)
        self.spo2_publisher = SpO2Publisher(lambda msg: self.logger.log(msg, "SpO2"), self.logger, spo2_topic)

        self.setup_data_displays_and_controls()
        
    def setup_data_displays_and_controls(self):
        """Data displays and corresponding controls"""
        # Create title frame
        title_frame = tk.Frame(self.master, width=400, borderwidth=2, relief="groove", padx=1, pady=5)
        title_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Broker url and port from config file
        tk.Label(title_frame, text="Publishing to Broker URL: " + config.MQTT_BROKER_URL, font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Label(title_frame, text="Port: " + str(config.MQTT_BROKER_PORT), font=("Arial", 10)).pack(side=tk.LEFT)

        self.status_bar = tk.Label(title_frame, text="Connection Status: Disconnected", font=("Arial", 10))
        # Check if already connected to the broker and update the status accordingly

        if self.heart_publisher.on_connect and self.bp_publisher.on_connect and self.spo2_publisher.on_connect:
            self.status_bar.config(text="Connection Status: Connected")

        # Connect button
        tk.Button(title_frame, text="Connect", command=self.connect, width=10).pack(side=tk.RIGHT)
        # Disconnect button
        tk.Button(title_frame, text="Disconnect", command=self.disconnect, width=10).pack(side=tk.RIGHT)

        # Create contents frame
        contents_frame = tk.Frame(self.master, width=400, borderwidth=2, relief="groove", padx=1, pady=5)
        contents_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        tk.Label(contents_frame, text="Contents", font=("Arial", 11)).pack()
        self.setup_topic_frame(1, "Heart Rate", self.heart_publisher)
        self.setup_topic_frame(2, "Blood Pressure", self.bp_publisher)
        self.setup_topic_frame(3, "SpO2", self.spo2_publisher)

    def setup_topic_frame(self, row, label, publisher):
        # Helper function to create a frame for each data topic.
        frame = tk.Frame(self.master, width=400, borderwidth=2, relief="groove", padx=1, pady=5)
        frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
        self.master.columnconfigure(0, weight=1) 
        tk.Label(frame, text=f"{label}", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
        display_label = tk.Label(frame, text="N/A", font=("Arial", 11))
        display_label.grid(row=0, column=1, sticky="w")

        # Setting up the log area for each publisher
        log_frame = tk.Frame(frame, borderwidth=2, relief="sunken", padx=10, pady=5)
        log_frame.grid(row=2, column=0, columnspan=4, rowspan=4, padx=10, pady=10, sticky='ew')
        log_text = ScrolledText(log_frame, height=6, width=100)
        log_text.pack(fill=tk.BOTH, expand=True)
        self.logger.register_log_widget(label, log_text)

        # make frame interactive when resizing
        frame.columnconfigure(0, weight=2)  
        frame.bind("<Configure>", lambda event: self.update_log_width(log_frame, event))

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
        tk.Button(frame, text=f"Send Wild Data", command=partial(self.send_wild_data, publisher, label), width=button_width).grid(row=4, column=8, padx=3, pady=3)
        tk.Button(frame, text=f"Skip Transmission", command=partial(self.skip_transmission, publisher, label), width=button_width).grid(row=5, column=8, padx=3, pady=3)

    def update_log_width(self, log_frame, event):
        # Update the width of the log frame based on the window size
        width = event.width - 20 
        log_frame.configure(width=width)

    def send_wild_data(self, publisher, label):
        try:
            self.logger.log(f"====================== Sending wild data for {label} ======================", label, tag='error')         
            publisher.send_wild_data() 
        except Exception as e:
            self.logger.log(f"Failed to send wild data for {label}: {str(e)}", label, tag="error")

    def skip_transmission(self, publisher, label):
        try:
            self.logger.log(f"====================== Skipping transmission for {label} ======================", label, tag='special')
            publisher.skip_transmissions(1)
        except Exception as e:
            self.logger.log(f"Failed to skip transmission for {label}: {str(e)}", label, tag="error")

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

    def connect(self):
        """Connect to the broker and update the connection status."""
        basepublisher.BasePublisher.on_connect = True
        self.heart_publisher.start()
        self.bp_publisher.start()
        self.spo2_publisher.start()
        self.status_bar.config(text="Connection Status: Connected")
        self.status_bar.pack()    

    def disconnect(self):
        """Disconnect from the broker and update the connection status."""
        self.heart_publisher.stop()
        self.bp_publisher.stop()
        self.spo2_publisher.stop()
        self.status_bar.config(text="Connection Status: Disconnected")
        self.status_bar.pack()

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.geometry("1100x650")
    root.resizable(True, True)
    root.mainloop()
