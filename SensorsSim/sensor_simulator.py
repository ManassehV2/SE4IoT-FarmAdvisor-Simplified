import os
import random
import paho.mqtt.client as mqtt
import time
import logging
from datetime import datetime, timedelta
from mysql_service import MySQLService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("sensor_simulator")

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "farms")

# Initialize MQTT client
mqtt_client = mqtt.Client()


def connect_to_mqtt():
    try:
        # Connect to the MQTT broker without authentication
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        mqtt_client.loop_start()  # Start the loop for handling communication
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        exit(1)


# Connect to MQTT
connect_to_mqtt()


# Fetch fields and sensors from the database
def fetch_fields_and_sensors():
    try:
        mysql_service = MySQLService()  # Initialize the MySQL service
        fields_with_sensors = mysql_service.get_all_fields_with_sensors()
        logger.info("Fetched fields and sensors from the database.")
        return fields_with_sensors
    except Exception as e:
        logger.error(f"Failed to fetch fields and sensors from database: {e}")
        return []


# Function to create sensor data
def create_sensor_data(sensor_serial, timestamp):
    # Generate realistic temperature
    temperature_actual = round(random.uniform(-10, 35), 2)
    raw_data = f"{sensor_serial},{timestamp},{temperature_actual}"
    logger.debug(
        f"Generated raw data for Sensor Serial {sensor_serial} at {timestamp}: {raw_data}")
    return raw_data


# Function to publish messages with error handling
def publish_message(topic, payload):
    try:
        # QoS=1 for acknowledgment
        result = mqtt_client.publish(topic, payload, qos=1)
        if result.rc != 0:
            logger.error(f"Publish failed with result code: {result.rc}")
        else:
            logger.info(f"Published to topic '{topic}': {payload}")
    except Exception as e:
        logger.error(f"Failed to publish message to topic '{topic}': {e}")


# Generate data for the past 20 days (including today) for all fields and sensors
def generate_past_20_days_data(fields_with_sensors, current_time):
    for field in fields_with_sensors:
        field_id = field.FieldId
        farm_id = field.FarmId
        topic = f"{MQTT_TOPIC_PREFIX}/{farm_id}/fields/{field_id}"

        for sensor in field.sensors:
            # Loop through the past 20 days including today
            for day_offset in range(21):
                day_time = current_time - timedelta(days=20 - day_offset)
                for hour_offset in range(24):  # Simulate 24 hours
                    timestamp = (day_time + timedelta(hours=hour_offset)
                                 ).strftime("%Y-%m-%d %H:%M:%S")
                    sensor_serial = sensor.SerialNo
                    raw_data = create_sensor_data(sensor_serial, timestamp)

                    publish_message(topic, raw_data)


# Main simulation loop
while True:
    current_time = datetime.now().replace(minute=0, second=0, microsecond=0)

    # Fetch the latest fields and sensors
    fields_with_sensors = fetch_fields_and_sensors()

    if fields_with_sensors:
        logger.info(
            "Generating past 20 days historical data (including today) for all fields and sensors.")
        generate_past_20_days_data(fields_with_sensors, current_time)

    time.sleep(int(os.getenv("DATA_GENERATION_INTERVAL_SEC", 60)))
