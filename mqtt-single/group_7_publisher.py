import json
import random
import time
from paho.mqtt import client as mqtt_client

class Publisher:
    def __init__(self, broker, port, topic, publish_interval=5, update_gui_callback=None):
        self.client_id = f'python-mqtt-publisher-{random.randint(0, 10000)}'
        self.broker = broker
        self.port = port
        self.topic = topic
        self.publish_interval = publish_interval  # New attribute for controlling speed
        self.client = mqtt_client.Client(self.client_id)
        self.update_gui_callback = update_gui_callback
        self.is_stopped = threading.Event()

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print(f"Failed to connect, return code {rc}\n")
        self.client.on_connect = on_connect
        self.client.connect(self.broker, self.port)

    def publish(self):
        self.connect_mqtt()
        self.client.loop_start()
        while not self.is_stopped.is_set():
            message = self.generate_health_data()
            result = self.client.publish(self.topic, message)
            if self.update_gui_callback:
                self.update_gui_callback(message)  # Update GUI with the published message (if callback provided)
            time.sleep(self.publish_interval)  # Use the interval specified during instantiation
        self.client.loop_stop()
        self.client.disconnect()

    def generate_health_data(self):
        # Heart Rate (BPM)
        heart_rate = random.randint(40, 200)  # Extended range for simulation
        
        # Blood Pressure (mmHg)
        systolic_bp = random.randint(80, 180)  # Extended range for simulation
        diastolic_bp = random.randint(40, 120)  # Extended range for simulation
        blood_pressure = f"{systolic_bp}/{diastolic_bp}"
        
        # Oxygen Saturation (SpO2 %)
        oxygen_saturation = random.randint(90, 100)  # Extended range for simulation

        data = {
            "timestamp": int(time.time()),
            "heart_rate": heart_rate,
            "blood_pressure": blood_pressure,
            "oxygen_saturation": oxygen_saturation
        }
        return json.dumps(data)

    def run(self, interval):
        self.connect_mqtt()
        self.client.loop_start()
        try:
            while True:
                self.publish()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Publisher is stopping...")
        finally:
            self.client.loop_stop()
