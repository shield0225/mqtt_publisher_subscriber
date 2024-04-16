import json
import random
import paho.mqtt.client as mqtt
import Utils.group_7_config as config
from Utils.group_7_SafeLogger import SafeLogger

class BasePublisher:
    def __init__(self, update_callback, logger, mqtt_topic):
        self.update_callback = update_callback
        self.active = False
        self.transmissions_to_skip = 0
        self.logger = logger  
        self.mqtt_topic = mqtt_topic
        print(f"Logger received in {self.__class__.__name__}: {self.logger}")

        self.setup_mqtt_client()

    def setup_mqtt_client(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.connect(config.MQTT_BROKER_URL, config.MQTT_BROKER_PORT, config.MQTT_KEEP_ALIVE_INTERVAL)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        label = self.__class__.__name__
        if rc == 0:
            self.logger.log("Connected to MQTT broker.", label)
        else:
            self.logger.log(f"Connection failed with result code {rc}.", label)

    def skip_transmissions(self, count):
        self.transmissions_to_skip += count

    def potentially_corrupt_data(self, data):
        # Randomly corrupt data
        chance_to_corrupt = 0.1  # 10% chance to corrupt data
        if random.random() < chance_to_corrupt:
            # Mutate the value to a negative number if corrupted
            data['value'] = -data['value']
            self.logger.log(f"Corrupted data detected, not published", self.__class__.__name__, tag="error")
        return data

    def publish_data(self, data, topic):
        if self.active and self.transmissions_to_skip <= 0:
            corrupted_data = self.potentially_corrupt_data(data)
            self.client.publish(topic, json.dumps(corrupted_data))
        elif self.transmissions_to_skip > 0:
            self.transmissions_to_skip -= 1
            self.logger.log(f"Skipped a transmission for {self.__class__.__name__}.")

    def stop(self):
        self.active = False
        self.client.disconnect()  # Disconnect from the broker
        self.logger.log(f"Disconnected from MQTT broker for {self.__class__.__name__}.")