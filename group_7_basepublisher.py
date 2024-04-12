import paho.mqtt.client as mqtt
import group_7_config as config
import group_7_SafeLogger as logger

class BasePublisher:
    def __init__(self, update_callback):
        self.update_callback = update_callback
        self.active = False
        self.transmissions_to_skip = 0
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.connect(config.MQTT_BROKER_URL, config.MQTT_BROKER_PORT)
        self.client.loop_start()
        self.logger = logger.SafeLogger()

    def stop(self):
        self.active = False

    def on_connect(self, rc):
        if rc == 0:
            self.logger.log(f"Connected to MQTT broker for {self.__class__.__name__}.", self.__class__.__name__)
        else:
            self.logger.log(f"Connection to MQTT broker failed with result code {rc} for {self.__class__.__name__}.", self.__class__.__name__)

    def skip_transmissions(self, count):
        self.transmissions_to_skip += count

    def publish_data(self, data):
        self.client.publish(self.config['MQTT_TOPIC'], data)