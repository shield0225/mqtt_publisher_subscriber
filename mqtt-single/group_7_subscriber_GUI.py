import tkinter as tk
from tkinter import scrolledtext, Frame
import threading
import json
import time
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from paho.mqtt import client as mqtt_client
from matplotlib.animation import FuncAnimation

class Subscriber:
    def __init__(self, master, broker, port, topic):
        self.master = master
        master.title("MQTT Subscriber GUI")

        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = f'python-mqtt-{random.randint(0, 10000)}'
        self.client = mqtt_client.Client(self.client_id)

        self.data = {'time': [], 'heart_rate': [], 'blood_pressure_systolic': [], 'blood_pressure_diastolic': [], 'oxygen_saturation': []}
        self.setup_gui()

        self.is_stopped = threading.Event()
        self.last_received = time.time()
        self.expected_interval = 5 + 2  # Publish interval plus a grace period

    def setup_gui(self):
        Frame(self.master).pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.log = scrolledtext.ScrolledText(self.master, height=10, width=50)
        self.log.pack(pady=10)
        self.log.tag_config("wild", foreground="red")
        self.log.tag_config("missed", foreground="blue")

        self.start_button = tk.Button(self.master, text="Start Listening", command=self.start_listening)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(self.master, text="Stop Listening", command=self.stop_listening)
        self.stop_button.pack(side=tk.RIGHT, padx=10)

        # Set up the matplotlib Figure and animate it
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.ani = FuncAnimation(self.figure, self.update_graph, interval=1000)

    def start_listening(self):
        self.is_stopped.clear()
        threading.Thread(target=self.listen).start()
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

    def stop_listening(self):
        self.is_stopped.set()
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.subscribe(self.topic)
                self.log.insert(tk.END, "Connected and subscribed to the topic.\n")
            else:
                self.log.insert(tk.END, f"Failed to connect, return code {rc}\n")
        self.client.on_connect = on_connect
        self.client.connect(self.broker, self.port)

    def listen(self):
        self.connect_mqtt()
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload.decode())
        current_time = time.time()
        if current_time - self.last_received > self.expected_interval:
            self.log.insert(tk.END, "Missed message detected.\n", "missed")
        self.display_message(message)
        self.last_received = current_time

    def display_message(self, message):
        if self.is_wild_data(message):
            self.log.insert(tk.END, f"Wild data detected: {json.dumps(message)}\n", "wild")
        else:
            display_text = f"Received: Heart Rate: {message['heart_rate']} BPM, "
            display_text += f"Blood Pressure: {message['blood_pressure']}, "
            display_text += f"Oxygen Saturation: {message['oxygen_saturation']}%\n"
            self.log.insert(tk.END, display_text)
        self.update_data(message)

    def update_data(self, message):
        # Append new data to the data dict
        bp_systolic, bp_diastolic = map(int, message['blood_pressure'].split('/'))
        self.data['time'].append(time.time())
        self.data['heart_rate'].append(message['heart_rate'])
        self.data['blood_pressure_systolic'].append(bp_systolic)
        self.data['blood_pressure_diastolic'].append(bp_diastolic)
        self.data['oxygen_saturation'].append(message['oxygen_saturation'])

    def update_graph(self, frame):
        # This function updates the graph
        if self.data['time']:
            self.ax.clear()
            self.ax.plot(self.data['time'], self.data['heart_rate'], label='Heart Rate')
            self.ax.plot(self.data['time'], self.data['blood_pressure_systolic'], label='Systolic BP')
            self.ax.plot(self.data['time'], self.data['blood_pressure_diastolic'], label='Diastolic BP')
            self.ax.plot(self.data['time'], self.data['oxygen_saturation'], label='Oxygen Saturation')
            self.ax.legend()
            self.canvas.draw()

    def is_wild_data(self, message):
        # Define conditions for wild data
        return message['heart_rate'] > 180 or message['oxygen_saturation'] < 80

if __name__ == "__main__":
    root = tk.Tk()
    app = Subscriber(root, 'localhost', 1883, 'health')
    root.mainloop()
