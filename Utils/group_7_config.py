# GUI Configuration
GUI_WINDOW_TITLE = "Health Data Publisher Simulator"
GUI_BG_COLOR = "#F0F0F0"
GUI_FONT = ("Arial", 12)
GUI_LOG_FONT = ("Courier New", 10)

# Publisher Configuration
TOPIC_HEART_RATE = "health/heart_rate"
TOPIC_BLOOD_PRESSURE = "health/blood_pressure"
TOPIC_OXYGEN_SATURATION = "health/spo2"

TRANSMISSION_ERROR_RATE = 1/100  # Approx. 1 in 100 transmissions will fail
WILD_DATA_RATE = 1/500  # Rare chance of sending wild data
SKIP_TRANSMISSION_RATE = 1/100  # Chance to skip a block of transmissions
SKIP_TRANSMISSION_BLOCK_MIN = 2  # Minimum number of transmissions to skip in a block
SKIP_TRANSMISSION_BLOCK_MAX = 5  # Maximum number of transmissions to skip in a block

# MQTT Broker Configuration 
MQTT_BROKER_URL = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_KEEP_ALIVE_INTERVAL = 60  # Seconds
