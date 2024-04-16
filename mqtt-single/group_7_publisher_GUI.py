import tkinter as tk
from tkinter import scrolledtext
import threading
import json
import random
import time
from paho.mqtt import client as mqtt_client

class Publisher:
    def __init__(self, master, broker, port, topic, publish_interval=5):
        self.master = master
        master.title("MQTT Publisher GUI")

        self.broker = broker
        self.port = port
        self.topic = topic
        self.publish_interval = publish_interval
        self.client_id = f'python-mqtt-{random.randint(0, 10000)}'
        self.client = mqtt_client.Client(self.client_id)

        self.setup_gui()

        self.is_stopped = threading.Event()

    def setup_gui(self):
        tk.Label(self.master, text="MQTT Publisher", font=("Arial", 16)).pack(pady=10)
        self.status_label = tk.Label(self.master, text="Status: Not connected")
        self.status_label.pack()

        self.log = scrolledtext.ScrolledText(self.master, height=10, width=50)
        self.log.pack(pady=10)

        self.start_button = tk.Button(self.master, text="Start Publishing", command=self.start_publishing)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(self.master, text="Stop Publishing", command=self.stop_publishing)
        self.stop_button.pack(side=tk.RIGHT, padx=10)

        self.wild_button = tk.Button(self.master, text="Send Wild Data", command=self.send_wild_data)
        self.wild_button.pack(side=tk.LEFT, padx=10)

    def start_publishing(self):
        self.is_stopped.clear()
        threading.Thread(target=self.publish).start()
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

    def stop_publishing(self):
        self.is_stopped.set()
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.status_label.config(text="Status: Connected")
            else:
                self.status_label.config(text=f"Status: Failed to connect, return code {rc}")
        self.client.on_connect = on_connect
        self.client.connect(self.broker, self.port)

    def publish(self):
        self.connect_mqtt()
        self.client.loop_start()
        while not self.is_stopped.is_set():
            message = self.generate_health_data()
            self.send_message(message)
            time.sleep(self.publish_interval)
        self.client.loop_stop()
        self.client.disconnect()

    def send_message(self, message):
        result = self.client.publish(self.topic, message)
        if result[0] == 0:
            log_message = f"Sent: {message}"
            self.log.insert(tk.END, log_message + '\n')
        else:
            self.log.insert(tk.END, "Failed to send message\n")

    def send_wild_data(self):
        wild_message = self.generate_wild_health_data()
        self.send_message(wild_message)

    def skip_transmission(self):
        # Do nothing, effectively skipping a transmission
        pass

    def generate_health_data(self):
        return json.dumps({
            "timestamp": int(time.time()),
            "heart_rate": random.randint(60, 100),
            "blood_pressure": f"{random.randint(110, 130)}/{random.randint(70, 85)}",
            "oxygen_saturation": random.randint(95, 100)
        })

    def generate_wild_health_data(self):
        return json.dumps({
            "timestamp": int(time.time()),
            "heart_rate": random.randint(200, 300),
            "blood_pressure": f"{random.randint(190, 210)}/{random.randint(120, 140)}",
            "oxygen_saturation": random.randint(50, 70)
        })

if __name__ == "__main__":
    root = tk.Tk()
    app = Publisher(root, 'localhost', 1883, 'health')
    root.mainloop()
