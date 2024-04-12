import random
import json
import threading
import time
from datetime import datetime
from group_7_basepublisher import BasePublisher

class HeartRatePublisher(BasePublisher):
    def __init__(self, update_callback, logger, publish_interval=3):
        super().__init__(update_callback)
        self.logger = logger
        self.publish_interval = publish_interval 
        self.active = False

    def start(self):
        if not self.active:
            self.active = True
            self.thread = threading.Thread(target=self.generate_data)
            self.thread.daemon = True  
            self.thread.start()
            self.logger.log(f"Starting data generation... publish interval = {self.publish_interval}", "Heart Rate")

    def stop(self):
        self.active = False
        self.logger.log("Stopping data generation...", "Heart Rate")

    def generate_data(self):
        while True:
            if not self.active:
                break  
            if self.transmissions_to_skip > 0:
                self.transmissions_to_skip -= 1
                continue
            heart_rate = random.randint(60, 100)
            timestamp = datetime.now().isoformat()
            data_package = {"timestamp": timestamp, "heart_rate": heart_rate}
            self.update_callback(json.dumps(data_package))
            time.sleep(self.publish_interval)
