import datetime
import json
import random
from datetime import datetime
import time

class BloodPressureDataGenerator:
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
                systolic = random.randint(90, 140)
                diastolic = random.randint(60, 90)
                timestamp = datetime.now().isoformat()
                data_package = {"timestamp": timestamp, "blood_pressure": [systolic, diastolic]}
                # Pass data to the callback
                self.update_callback(json.dumps(data_package))
        except Exception as e:
            self.update_callback(json.dumps({"error": str(e)}))
            self.active = False 

    def send_wild_data(self):
        # Extremely high or low blood pressure
        wild_systolic = random.choice([random.randint(50, 89), random.randint(181, 240)])
        wild_diastolic = random.choice([random.randint(20, 59), random.randint(121, 180)])
        timestamp = datetime.now().isoformat()
        wild_data = {"timestamp": timestamp, "blood_pressure": [wild_systolic, wild_diastolic]}
        self.update_callback(json.dumps(wild_data))

    def skip_transmission(self, count):
        self.transmissions_to_skip += count