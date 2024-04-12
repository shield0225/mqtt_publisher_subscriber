import random
import json
import threading
import time
from datetime import datetime
from group_7_basepublisher import BasePublisher

class SpO2Publisher(BasePublisher):
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
            self.logger.log(f"Starting data generation... publish interval = {self.publish_interval}", "SpO2")

    def stop(self):
        self.active = False
        self.logger.log("Stopping data generation...", "SpO2")

    def generate_data(self):
        while True:
            if not self.active:
                break  
            if self.transmissions_to_skip > 0:
                self.transmissions_to_skip -= 1
                continue
            spo2 = random.randint(90, 100)
            timestamp = datetime.now().isoformat()
            data_package = {"timestamp": timestamp, "spO2": spo2}
            self.update_callback(json.dumps(data_package))
            time.sleep(self.publish_interval)
