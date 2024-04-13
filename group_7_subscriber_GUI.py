import tkinter as tk
from tkinter import ttk, scrolledtext
from paho.mqtt import client as mqtt_client
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

broker = 'localhost'  # Change to your broker's IP
port = 1883
topics = {
    "Heart Rate": "health/heart_rate",
    "Blood Pressure": "health/blood_pressure",
    "SpO2": "health/spo2"
}

class HealthSubscriber:
    def __init__(self, master):
        self.master = master
        self.master.title("Health Data Subscriber")

        self.setup_gui()
        
        self.client = mqtt_client.Client("SubscriberClient")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port)
        self.client.loop_start()
        
        self.data_queue = deque(maxlen=50)  # Store last 50 data points for plotting

    def setup_gui(self):
        # Log text widget
        self.log_text = scrolledtext.ScrolledText(self.master, height=10, width=50)
        self.log_text.grid(row=2, column=0, padx=10, pady=10)

        # Topic selection ComboBox
        self.topic_var = tk.StringVar()
        self.topic_var.set("Select Topic")
        self.combobox = ttk.Combobox(self.master, textvariable=self.topic_var, values=list(topics.keys()), state="readonly")
        self.combobox.grid(row=0, column=0, padx=10, pady=10)
        self.combobox.bind("<<ComboboxSelected>>", self.subscribe_topic)

        # Data display label
        self.display_label = tk.Label(self.master, text="Waiting for data...", font=('Arial', 14))
        self.display_label.grid(row=1, column=0, padx=10, pady=10)

        # Graph setup
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'r-')  # Initialize an empty line
        self.ax.set_xlim(0, 50)  # Set the initial x-axis limits
        self.ax.set_ylim(0, 150)  # Set the initial y-axis limits based on expected data ranges
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=3, column=0, padx=10, pady=10)

        # Set grid weights
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(3, weight=1)

    def on_connect(self, client, userdata, flags, rc):
        if hasattr(self, 'log_text'):  # Ensure log_text is available
            self.log_text.insert(tk.END, f"Connected with result code {str(rc)}\n")
            self.log_text.see(tk.END)
        else:
            print("Connection successful, but log_text not initialized.")

    def subscribe_topic(self, event):
        topic = topics[self.topic_var.get()]
        self.client.unsubscribe(list(topics.values()))  # Unsubscribe all before subscribing new
        self.client.subscribe(topic)
        self.log_text.insert(tk.END, f"Subscribed to {self.topic_var.get()}\n")
        self.display_label.config(text=f"Subscribed to {self.topic_var.get()}")

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            topic = msg.topic
            # Log the received message along with the topic
            self.log_message(f"Received message on {topic}: {data}")
            # Update the GUI display based on the data received
            self.update_display(data)
        except json.JSONDecodeError as e:
            self.log_message(f"Error decoding JSON: {str(e)}")
        except Exception as e:
            self.log_message(f"Error processing message: {str(e)}")


    def update_display(self, data):
        value = 0
        if 'heart_rate' in data:
            value = data['heart_rate']
            self.display_label.config(text=f"Heart Rate: {value} bpm")
        elif 'blood_pressure' in data:
            systolic, diastolic = data['blood_pressure']
            value = systolic  # example to plot systolic pressure
            self.display_label.config(text=f"Blood Pressure: {systolic}/{diastolic} mmHg")
        elif 'spO2' in data:
            value = data['spO2']
            self.display_label.config(text=f"SpO2: {value}%")

        self.data_queue.append(value)
        self.update_graph()

    def update_graph(self):
        y_data = list(self.data_queue)
        x_data = range(len(y_data))
        self.line.set_data(x_data, y_data)
        self.ax.relim()  # Recompute the data limits
        self.ax.autoscale_view()  # Automatically scale the view to the data
        self.canvas.draw()

    def log_message(self, message):
        """Log a message to the ScrolledText widget safely."""
        if hasattr(self, 'log_text'):  # Check if log_text is already initialized
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
        else:
            print(message)  # Fallback to printing to console if GUI isn't ready

if __name__ == '__main__':
    root = tk.Tk()
    app = HealthSubscriber(root)
    root.mainloop()
