import random
import json
import time
from datetime import datetime
from group_7_SafeLogger import SafeLogger

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
                if self.transmissions_to_skip > 0:
                    self.transmissions_to_skip -= 1
                    continue
                heart_rate = random.randint(60, 100)
                timestamp = datetime.now().isoformat()
                data_package = {"timestamp": timestamp, "heart_rate": heart_rate}
                # Pass data to the callback function
                self.update_callback(json.dumps(data_package))
                time.sleep(self.publish_interval)
        except Exception as e:
            self.logger.log(f"Error in generating data: {str(e)}", "Heart Rate")
            self.active = False  

    def send_wild_data(self):
        # Extremely high or low heart rate
        wild_heart_rate = random.choice([random.randint(50, 59), random.randint(101, 140)])
        data = json.dumps({"heart_rate": wild_heart_rate})
        self.update_callback(data)

    def skip_transmission(self, count):
        self.transmissions_to_skip += count

class BloodPressureDataGenerator:
    def __init__(self, update_callback, publish_interval=3):
        self.update_callback = update_callback
        self.publish_interval = publish_interval
        self.active = False
        self.transmissions_to_skip = 0
    
    def generate_data(self):
        try:
            while self.active:
                if self.transmissions_to_skip > 0:
                    self.transmissions_to_skip -= 1
                    continue
                systolic = random.randint(90, 140)
                diastolic = random.randint(60, 90)
                timestamp = datetime.now().isoformat()
                data_package = {"timestamp": timestamp, "blood_pressure": [systolic, diastolic]}
                # Pass data to the callback
                self.update_callback(json.dumps(data_package))
                time.sleep(self.publish_interval)
        except Exception as e:
            self.update_callback(json.dumps({"error": str(e)}))
            self.active = False 

    def send_wild_data(self):
        # Extremely high or low blood pressure
        wild_systolic = random.choice([random.randint(50, 89), random.randint(181, 240)])
        wild_diastolic = random.choice([random.randint(20, 59), random.randint(121, 180)])
        data = json.dumps({"blood_pressure": [wild_systolic, wild_diastolic]})
        self.update_callback(data)

    def skip_transmission(self, count):
        self.transmissions_to_skip += count

class Sp02DataGenerator:
    def __init__(self, update_callback, publish_interval=3):
        self.update_callback = update_callback
        self.publish_interval = publish_interval
        self.active = False
        self.transmissions_to_skip = 0

    def generate_data(self):
        try:
            while self.active:
                if self.transmissions_to_skip > 0:
                    self.transmissions_to_skip -= 1
                    continue
                spo2 = random.randint(90, 100)
                timestamp = datetime.now().isoformat()
                data_package = {"timestamp": timestamp, "spO2": spo2}
                # Pass data to the callback
                self.update_callback(json.dumps(data_package))
                time.sleep(self.publish_interval)
        except Exception as e:
            self.update_callback(json.dumps({"error": str(e)}))
            self.active = False 

    def send_wild_data(self):
        # Extremely low SpO2 levels
        wild_spo2 = random.randint(50, 74)
        data = json.dumps({"spO2": wild_spo2})
        self.update_callback(data)

    def skip_transmission(self, count):
        self.transmissions_to_skip += count