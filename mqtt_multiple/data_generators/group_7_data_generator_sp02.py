import datetime
import json
import random
from datetime import datetime
import time

class Sp02DataGenerator:
    def __init__(self, update_callback, publish_interval=3):
        self.update_callback = update_callback
        self.publish_interval = publish_interval
        self.active = False
        self.transmissions_to_skip = 0

    def generate_data(self):
        try:
            while self.active:
                time.sleep(self.publish_interval) # Wait for the next data transmission
                if self.transmissions_to_skip > 0:
                    self.transmissions_to_skip -= 1
                    continue
                spo2 = random.randint(90, 100)
                timestamp = datetime.now().isoformat()
                data_package = {"timestamp": timestamp, "spO2": spo2}
                # Pass data to the callback
                self.update_callback(json.dumps(data_package))
        except Exception as e:
            self.update_callback(json.dumps({"error": str(e)}))
            self.active = False 

    def send_wild_data(self):
        # Extremely low SpO2 levels
        wild_spo2 = random.randint(50, 74)
        timestamp = datetime.now().isoformat()
        wild_data = {"timestamp": timestamp, "spO2": wild_spo2}
        self.update_callback(json.dumps(wild_data))

    def skip_transmission(self, count):
        self.transmissions_to_skip += count