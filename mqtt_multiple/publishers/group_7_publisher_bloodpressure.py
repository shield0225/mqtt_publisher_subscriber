import threading
from publishers.group_7_basepublisher import BasePublisher
from data_generators.group_7_data_generator_bloodpressure import BloodPressureDataGenerator

class BloodPressurePublisher(BasePublisher):
    def __init__(self, update_callback, logger, mqtt_topic):
        super().__init__(update_callback, logger, mqtt_topic)
        self.logger = logger
        self.active = False
        self.topic = mqtt_topic
        self.publish_interval = 3
        self.data_generator = BloodPressureDataGenerator(self.publish_data, self.publish_interval)

    def publish_data(self, data):
        """Callback to publish data using MQTT."""
        if self.active:
            try:
                self.client.publish(self.topic, data)
                self.logger.log(f"Published data: {data}", "Blood Pressure")
            except Exception as e:
                self.logger.log(f"Corrupted data detected, not published", "Blood Pressure", tag="error")

    def start(self):
        """Start the data generation and publishing process."""
        if not self.active:
            self.active = True
            self.logger.log(f"Attempting to start data generation with interval: {self.publish_interval}", "Blood Pressure")
            self.data_generator.active = True
            self.logger.log("Starting data generation and publisher...", "Blood Pressure")
            thread = threading.Thread(target=self.data_generator.generate_data)
            thread.daemon = True
            thread.start()
            self.logger.log("Data generation started.", "Blood Pressure")

    def stop(self):
        """Stop the data generation and publishing process."""
        self.data_generator.active = False
        self.active = False
        self.logger.log("Stopping data generation...", "Blood Pressure")

    def send_wild_data(self):
        """Send wild data to the callback function."""
        try:
            wild_data = self.data_generator.send_wild_data()
            self.client.publish(self.topic, wild_data)
            self.logger.log(f"Publisher sent wild data", "Blood Pressure", tag="error")
        except Exception as e:
            self.logger.log(f"Unexpected error publishing wild data: {str(e)}", "Blood Pressure", tag="error")

    def skip_transmissions(self, count):
        """Skip a specified number of transmissions."""
        self.data_generator.skip_transmission(count)
        self.logger.log(f"Skipped {count} transmissions.", "Blood Pressure", tag="special")


