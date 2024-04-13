import threading
from group_7_basepublisher import BasePublisher
from group_7_data_generator import HeartRateDataGenerator

class HeartRatePublisher(BasePublisher):
    def __init__(self, update_callback, logger, mqtt_topic):
        super().__init__(update_callback, logger, mqtt_topic)
        self.logger = logger
        self.active = False
        self.topic = mqtt_topic
        self.publish_interval = 3
            
        self.data_generator = HeartRateDataGenerator(self.publish_data, self.publish_interval, self.logger)

    def publish_data(self, data):
        """Callback to publish data using MQTT."""
        if self.active:
            try:
                self.client.publish(self.topic, data)
                self.logger.log(f"Published data: {data}", "Heart Rate")
            except Exception as e:
                self.logger.log(f"Failed to publish data: {str(e)}", "Heart Rate")

    def start(self):
        """Start the data generation and publishing process."""
        if not self.active:
            self.active = True
            self.logger.log(f"Attempting to start data generation with interval: {self.publish_interval}", "Heart Rate")
            self.data_generator.active = True
            self.logger.log("Starting data generation and publisher...", "Heart Rate")
            thread = threading.Thread(target=self.data_generator.generate_data)
            thread.daemon = True
            thread.start()
            self.logger.log("Data generation started.", "Heart Rate")

    def stop(self):
        """Stop the data generation and publishing process."""
        self.data_generator.active = False
        self.active = False
        self.logger.log("Stopping data generation...", "Heart Rate")
