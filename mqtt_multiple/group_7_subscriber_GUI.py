import tkinter as tk
from tkinter import ttk, scrolledtext
from paho.mqtt import client as mqtt_client
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import time
from datetime import datetime

broker = 'localhost'  
port = 1883
topics = {
    "Heart Rate": "health/heart_rate",
    "Blood Pressure": "health/blood_pressure",
    "SpO2": "health/spo2"
}
expected_intervals = {
    "health/heart_rate": 1,   
    "health/blood_pressure": 3,  
    "SpO2": 5  
}

class HealthSubscriber:
    def __init__(self, master):
        self.master = master
        self.master.title("Health Data Subscriber")

        self.last_received_time = {}  # Track the last receive time for each topic
        self.topic_labels = {} # Store the labels for each topic
        self.line_objects = {} # Store the line objects for each topic
        self.data_queues = {
            topics["Heart Rate"]: deque(maxlen=50),
            topics["Blood Pressure"] + '_systolic': deque(maxlen=50),
            topics["Blood Pressure"] + '_diastolic': deque(maxlen=50),
            topics["SpO2"]: deque(maxlen=50)
        }

        self.setup_gui()
      
        self.client = mqtt_client.Client("SubscriberClient")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port)
        self.client.loop_start()
        
        self.active_subscriptions = set() 
        self.last_received_time = {}  
        self.last_value_time = {}

    def setup_gui(self):
        large_font = ('Arial', 14)  

        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)

        row = 0
        for topic_name in topics.keys():
            # Checkbox for each topic
            var = tk.BooleanVar()
            cb = tk.Checkbutton(self.master, text=topic_name, variable=var, font=large_font,
                                command=lambda t=topics[topic_name], v=var: self.subscribe_or_unsubscribe(t, v))
            cb.grid(row=row, column=0, sticky='w')

            # Label for each topic
            label = tk.Label(self.master, text=f"Waiting for data...", font=large_font)
            label.grid(row=row, column=1, padx=10, pady=10, sticky='ew')
            self.topic_labels[topic_name] = label
            row += 1

        # Text box for logging should span both columns
        self.log_text = scrolledtext.ScrolledText(self.master, height=10, width=75, font=large_font)
        self.log_text.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        row += 1

        # Anomaly log text widget should also span both columns
        self.anomaly_log_text = scrolledtext.ScrolledText(self.master, height=5, width=75, font=large_font)
        self.anomaly_log_text.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        row += 1

        # Canvas for plotting should span both columns as well
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.lines = {}
        colors = {'health/heart_rate': 'r', 'health/blood_pressure_systolic': 'b', 'health/blood_pressure_diastolic': 'g', 'health/spo2': 'purple'}
        for topic in topics.values():
            if topic == 'health/blood_pressure':
                # Create two lines for blood pressure
                self.lines[topic + '_systolic'], = self.ax.plot([], [], label=topic.split('/')[-1] + ' Systolic', color=colors[topic + '_systolic'])
                self.lines[topic + '_diastolic'], = self.ax.plot([], [], label=topic.split('/')[-1] + ' Diastolic', color=colors[topic + '_diastolic'])
            else:
                self.lines[topic], = self.ax.plot([], [], label=topic.split('/')[-1], color=colors[topic])
        self.ax.legend()
        self.ax.set_xlim(0, 50)
        self.ax.set_ylim(0, 150)  # Adjust y-axis limit based on expected data range
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=10, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            message = "Connected successfully to MQTT broker."
        else:
            message = f"Failed to connect, return code {rc}"
        
        # Log the connection message in your GUI and print it
        self.master.after(0, self.log_message, message)
        self.master.after(0, self.update_gui_with_message, message)

    def subscribe_or_unsubscribe(self, topic, var):
        derived_topic_systolic = topic + '_systolic'
        derived_topic_diastolic = topic + '_diastolic'
        if var.get():  # If the checkbox is checked, subscribe to the topic
            self.client.subscribe(topic)
            self.active_subscriptions.add(topic)
            self.active_subscriptions.add(derived_topic_systolic)
            self.active_subscriptions.add(derived_topic_diastolic)
            self.log_message(f"Subscribed to {topic}, {derived_topic_systolic}, and {derived_topic_diastolic}")
        else:  # If the checkbox is unchecked, unsubscribe from the topic
            self.client.unsubscribe(topic)
            self.active_subscriptions.discard(topic)
            self.active_subscriptions.discard(derived_topic_systolic)
            self.active_subscriptions.discard(derived_topic_diastolic)
            self.log_message(f"Unsubscribed from {topic}, {derived_topic_systolic}, and {derived_topic_diastolic}")

    def log_message(self, message):
        # Assuming you have initialized self.log_text elsewhere in your setup_gui method
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)

    def update_gui_with_message(self, message):
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        else:
            print("Log text widget not available:", message)

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        current_time = time.time()
        
        try:
            data = json.loads(msg.payload.decode())
            print(f"Received data on {topic}: {data}")  

            # Only process messages for topics that are actively subscribed to
            if topic not in self.active_subscriptions:
                return  # Skip processing for unsubscribed topics

            # Logging the received message
            self.log_message(f"Received message on {topic}: {data}")

            # Check for wild data
            if self.is_wild_data(data, topic):
                self.log_message(f"Wild data on {topic}: {data}")
                self.anomaly_log_text.insert(tk.END, f"Excluded wild data on {topic} at {current_time}: {data}\n")
                self.anomaly_log_text.see(tk.END)
                return  # Skip further processing of this message

            self.log_message(f"Received message on {topic}: {data}")

            # Handling Heart Rate data
            if topic == topics["Heart Rate"]:
                heart_rate = data.get('heart_rate')
                if heart_rate is not None:
                    self.data_queues[topic].append((heart_rate, current_time))
                    self.update_display(topic, data)

            # Handling Blood Pressure data
            elif topic == topics["Blood Pressure"]:
                blood_pressure = data.get('blood_pressure')
                if blood_pressure and len(blood_pressure) == 2:
                    systolic, diastolic = blood_pressure
                    self.data_queues[topic + '_systolic'].append((systolic, current_time))
                    self.data_queues[topic + '_diastolic'].append((diastolic, current_time))
                    self.update_display(topic, data)

            # Handling SpO2 data
            elif topic == topics["SpO2"]:
                spO2 = data.get('spO2')
                if spO2 is not None:
                    self.data_queues[topic].append((spO2, current_time))
                    self.update_display(topic, data)

                # Update the graph after new data has been appended
                self.update_graph()
            else:
                self.log_message(f"Excluded wild data on {topic}: {data}")

        except json.JSONDecodeError as e:
            self.log_message(f"Error decoding JSON: {str(e)}")
        except KeyError as e:
            self.log_message(f"Data key error: {str(e)}")  # Handles missing keys in data dictionaries
        except Exception as e:
            self.log_message(f"Unhandled error: {str(e)}")  # General catch-all for any other exceptions


    def check_for_wild_data(self, data, topic):
        wild = False
        if topic == topics["Heart Rate"] and (data['heart_rate'] < 60 or data['heart_rate'] > 100):
            wild = True
        elif topic == topics["Blood Pressure"] and (data['blood_pressure'][0] > 180 or data['blood_pressure'][1] < 50):
            wild = True
        elif topic == topics["SpO2"] and (data['spO2'] < 85):
            wild = True
        
        if wild:
            self.anomaly_button.config(bg='red')
            self.anomaly_log_text.insert(tk.END, f"Wild data detected: {data} on topic {topic}\n")
            self.anomaly_log_text.see(tk.END)

    def reset_graph(self):
        """Resets the graph to its initial empty state."""
        self.data_queue.clear()  # Clear the data queue
        self.ax.clear()  # Clear the plot
        
        # Reinitialize the plot settings
        self.ax.set_xlim(0, 50)
        self.ax.set_ylim(0, 150)
        self.line, = self.ax.plot([], [], 'r-')  # Re-create the line object
        
        self.canvas.draw()  # Redraw the canvas to show the cleared state

    def is_wild_data(self, data, topic):
        if topic == topics["Heart Rate"] and (data['heart_rate'] < 60 or data['heart_rate'] > 100):
            return True
        elif topic == topics["Blood Pressure"] and (data['blood_pressure'][0] > 180 or data['blood_pressure'][1] < 50):
            return True
        elif topic == topics["SpO2"] and (data['spO2'] < 85):
            return True
        return False

    def mark_missed_message(self, topic, elapsed_time):
        missed_time = self.last_received_time[topic] + expected_intervals[topic]
        # Log the missed message
        self.anomaly_log_text.insert(tk.END, f"Missed transmission detected for {topic} at {datetime.fromtimestamp(missed_time)}\n")
        self.anomaly_log_text.see(tk.END)
        # Append a special value (e.g., None) to mark a gap in the data queue
        if topic in self.data_queues:
            self.data_queues[topic].append((None, missed_time))

    def update_display(self, topic, data):
        # Dynamically update the label corresponding to the topic with new data
        topic_name = next(key for key, value in topics.items() if value == topic)
        if topic_name in self.topic_labels:
            if topic == topics["Heart Rate"]:
                self.topic_labels[topic_name].config(text=f"Heart Rate: {data['heart_rate']} bpm")
            elif topic == topics["Blood Pressure"]:
                systolic, diastolic = data['blood_pressure']
                self.topic_labels[topic_name].config(text=f"Blood Pressure: {systolic}/{diastolic} mmHg")
            elif topic == topics["SpO2"]:
                self.topic_labels[topic_name].config(text=f"SpO2: {data['spO2']}%")

        self.update_graph()

    def update_graph(self):
        # Ensure we process the correct queue lengths and handle potential empty queues
        for topic, line in self.lines.items():
            data_queue = self.data_queues[topic]
            x_data = list(range(len(data_queue)))  # x data should be the index count of data points
            y_data = [data[0] for data in data_queue if data is not None]  # y data from the queue, filtering out None

            if len(x_data) != len(y_data):
                # This should not happen, but in case it does, log an error or handle it.
                print(f"Data length mismatch for topic {topic}: x_data {len(x_data)}, y_data {len(y_data)}")
                continue  # Skip this iteration to avoid plotting errors

            line.set_data(x_data, y_data)  # Update the line data

        # Adjust plot limits and refresh
        self.ax.relim()  # Recalculate limits
        self.ax.autoscale_view(True, True, True)  # Autoscale view to include all data
        self.canvas.draw()  # Redraw the canvas to update the plot


    def log_message(self, message):
        """Log a message to the ScrolledText widget safely."""
        if hasattr(self, 'log_text'):  
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
        else:
            print(message)  

    def on_closing(self):
        """Called when the window is closed."""
        self.client.disconnect() 
        self.client.loop_stop() 
        self.master.destroy() 

if __name__ == '__main__':
    root3 = tk.Tk()
    app3 = HealthSubscriber(root3)
    root3.geometry(f'600x950')
    root3.protocol("WM_DELETE_WINDOW", app3.on_closing)
    root3.mainloop()