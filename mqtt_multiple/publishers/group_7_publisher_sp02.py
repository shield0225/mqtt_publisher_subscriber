import threading
from publishers.group_7_basepublisher import BasePublisher
from data_generators.group_7_data_generator_sp02 import Sp02DataGenerator

class SpO2Publisher(BasePublisher):
    def __init__(self, update_callback, logger, mqtt_topic):
        super().__init__(update_callback, logger, mqtt_topic)
        self.logger = logger
        self.active = False
        self.topic = mqtt_topic
        self.publish_interval = 5
        self.data_generator = Sp02DataGenerator(self.publish_data, self.publish_interval)

    def publish_data(self, data):
        """Callback to publish data using MQTT."""
        if self.active:
            try:
                self.client.publish(self.topic, data)
                self.logger.log(f"Published data: {data}", "SpO2")
            except Exception as e:
                self.logger.log(f"Corrupted data detected, not published", "SpO2", tag="error")

    def start(self):
        """Start the data generation and publishing process."""
        if not self.active:
            self.active = True
            self.logger.log(f"Attempting to start data generation with interval: {self.publish_interval}", "SpO2")
            self.data_generator.active = True
            self.logger.log("Starting data generation and publisher...", "SpO2")
            thread = threading.Thread(target=self.data_generator.generate_data)
            thread.daemon = True
            thread.start()
            self.logger.log("Data generation started.", "SpO2")

    def stop(self):
        """Stop the data generation and publishing process."""
        self.data_generator.active = False
        self.active = False
        self.logger.log("Stopping data generation...", "SpO2")

    def send_wild_data(self):
        """Send wild data to the callback function."""
        try:
            wild_data = self.data_generator.send_wild_data()
            self.client.publish(self.topic, wild_data)
            self.logger.log(f"Publisher sent wild data", "SpO2", tag="error")
        except Exception as e:
            self.logger.log(f"Unexpected error publishing wild data: {str(e)}", "SpO2", tag="error")

    def skip_transmissions(self, count):
        """Skip a specified number of transmissions."""
        self.data_generator.skip_transmission(count)
        self.logger.log(f"Skipped {count} transmissions.", "Sp02", tag="special")    

