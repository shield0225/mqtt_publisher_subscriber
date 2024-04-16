import json
import random
from paho.mqtt import client as mqtt_client

class Subscriber:
    def __init__(self, broker, port, topic):
        self.client_id = f'python-mqtt-subscriber-{random.randint(0, 10000)}'
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt_client.Client(self.client_id)

        # Setting the on_message callback within the class
        self.client.on_message = self.on_message

    def on_message(self, client, userdata, msg):
        # Parsing the message payload
        message = json.loads(msg.payload.decode())
        print(f"Received data on {msg.topic}:")
        print(f"Heart Rate: {message['heart_rate']} BPM")
        print(f"Blood Pressure: {message['blood_pressure']} mmHg")
        print(f"Oxygen Saturation: {message['oxygen_saturation']}%")
        print("")

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                client.subscribe(self.topic)
            else:
                print(f"Failed to connect, return code {rc}\n")
        self.client.on_connect = on_connect
        self.client.connect(self.broker, self.port)

    def run(self):
        self.connect_mqtt()
        self.client.loop_forever()
