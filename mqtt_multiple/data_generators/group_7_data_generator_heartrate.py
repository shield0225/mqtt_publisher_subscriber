import random
import json
import time
from datetime import datetime
from Utils.group_7_SafeLogger import SafeLogger

class HeartRateDataGenerator:
    def __init__(self, update_callback, publish_interval, logger):
        self.update_callback = update_callback
        self.publish_interval = publish_interval
        self.active = False
        self.transmissions_to_skip = 0
        self.logger = logger  

    def generate_data(self):
        try:
            while self.active:
                time.sleep(self.publish_interval) # Wait for the next data transmission
                if self.transmissions_to_skip > 0:
                    self.transmissions_to_skip -= 1
                    continue
                heart_rate = random.randint(60, 100)
                timestamp = datetime.now().isoformat()
                data_package = {"timestamp": timestamp, "heart_rate": heart_rate}
                # Pass data to the callback function
                self.update_callback(json.dumps(data_package))
        except Exception as e:
            self.logger.log(f"Error in generating data: {str(e)}", "Heart Rate")
            self.active = False  

    def send_wild_data(self):
        # Extremely high or low heart rate
        wild_heart_rate = random.choice([random.randint(50, 59), random.randint(101, 140)])
        timestamp = datetime.now().isoformat()
        wild_data = {"timestamp": timestamp, "heart_rate": wild_heart_rate}
        self.update_callback(json.dumps(wild_data))

    def skip_transmission(self, count):
        self.transmissions_to_skip += count
