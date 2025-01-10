import os
import logging
import time
from datetime import datetime
import threading
import requests
import paho.mqtt.client as mqtt
from azure_table_service import AzureTableService
from mysql_service.service import MySQLService

# Environment Variables
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "farms")
BASE_WEATHER_API_URL = os.getenv(
    "BASE_WEATHER_API_URL", "https://api.met.no/weatherapi/locationforecast/2.0")
GET_FORECAST_INTERVAL_SEC = int(os.getenv("GET_FORECAST_INTERVAL_SEC", 60))

# Initialize services
table_service = AzureTableService()
mysql_service = MySQLService()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MQTT Handlers


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker")
        client.subscribe(f"{MQTT_PREFIX}/#")
        logger.info(f"Subscribed to topics with prefix {MQTT_PREFIX}")
    else:
        logger.error(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    logger.info(f"Received message from topic {msg.topic}")

    try:
        # Decode the MQTT message payload
        message_body = msg.payload.decode("utf-8")
        logger.info(f"Raw message body: {message_body}")

        # Split the CSV data
        sensor_serial, timestamp, temperature_actual = message_body.split(',')

        # Prepare sensor data for storage
        sensor_data = {
            "sensor_serial": sensor_serial,
            "timestamp": datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
            "temperature_actual": float(temperature_actual),
        }
        logger.info(f"Decoded sensor data: {sensor_data}")

        # Use AzureTableService to store the data
        table_service = AzureTableService()

        table_name = "weatherdata"

        # Ensure the table exists
        table_service.create_table_if_not_exists(table_name)

        # Prepare the entity with sensor data fields
        entity = {
            "PartitionKey": sensor_data['sensor_serial'],
            "RowKey": sensor_data['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
            "temperature_actual": sensor_data["temperature_actual"],
        }

        # Store the entity in the table
        table_service.store_entity(table_name, entity)
        logger.info(
            f"Stored entity for sensor_serial {sensor_data['sensor_serial']}")

    except ValueError as e:
        logger.error(f"Failed to parse CSV data: {e}")
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}")


# MQTT Client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Scheduled Function (Weather Forecast)


def fetch_weather_forecast():
    while True:
        try:
            logger.info("Executing scheduled weather forecast task...")
            # Fetch all fields and their sensors from MySQL
            fields_with_sensors = mysql_service.get_all_fields_with_sensors()
            logger.info(f"Fetched fields with sensors: {fields_with_sensors}")

            for field in fields_with_sensors:
                logger.info(
                    f"Processing field: {field.Name}, Altitude: {field.Altitude}")

                for sensor in field.sensors:
                    sensor_serial_number = sensor.SerialNo
                    lat = sensor.Lat
                    lon = sensor.Long

                    logger.info(
                        f"Fetching forecast data for sensor {sensor_serial_number} at location ({lat}, {lon})")

                    # Fetch forecast data from Weather API
                    url = f"{BASE_WEATHER_API_URL}/compact?lat={lat}&lon={lon}"
                    logger.info(f"Constructed URL: {url}")

                    try:
                        response = requests.get(
                            url, headers={"User-Agent": "gdd/1.0 (user@gdd.com)"})
                        response.raise_for_status()
                        met_api_response = response.json()

                        forecast_data = []
                        for item in met_api_response["properties"]["timeseries"]:
                            timestamp_str = item["time"].replace('Z', '+00:00')
                            timestamp = datetime.fromisoformat(timestamp_str)

                            # Dynamically use all data in `instant/details`
                            instant_details = item["data"]["instant"]["details"]

                            # Add PartitionKey and RowKey for Azure Table Storage
                            instant_details["PartitionKey"] = sensor_serial_number
                            instant_details["RowKey"] = timestamp.strftime(
                                "%Y-%m-%d %H:%M:%S")

                            forecast_data.append(instant_details)

                        # Save all forecast data for this sensor
                        if forecast_data:
                            table_service.save_weather_data_list(forecast_data)
                            logger.info(
                                f"Successfully stored {len(forecast_data)} forecast entries for sensor {sensor_serial_number}")
                        else:
                            logger.warning(
                                f"No valid forecast data to save for sensor {sensor_serial_number}.")

                        # Calculate GDD data and update cutting date in MySQL
                        table_service.add_gdd_forecast(sensor_serial_number)
                        table_service.add_gdd_actual(sensor_serial_number)

                        # Computation of the CuttingDateCalculated of each sensor
                        calculatedCuttingDate = table_service.calculate_cutting_date(
                            sensor_serial_number, sensor.OptimalGDD, mysql_service.get_latest_sensor_reset_date_by_serial(sensor_serial_number))

                        mysql_service.update_sensor_cutting_date(
                            sensor_serial_number, calculatedCuttingDate)

                    except requests.RequestException as e:
                        logger.error(
                            f"HTTP request failed for sensor {sensor_serial_number}: {e}")
                    except KeyError as e:
                        logger.error(
                            f"Error parsing response for sensor {sensor_serial_number}: missing key {e}")
                    except Exception as e:
                        logger.error(
                            f"Unexpected error for sensor {sensor_serial_number}: {e}")

            time.sleep(GET_FORECAST_INTERVAL_SEC)
        except Exception as e:
            logger.error(f"Error in weather forecast task: {e}")


# Main Execution
if __name__ == "__main__":
    # Start MQTT Client in a separate thread
    threading.Thread(target=client.connect, args=(
        MQTT_BROKER, MQTT_PORT)).start()
    threading.Thread(target=client.loop_forever).start()

    # Start scheduled task
    fetch_weather_forecast()
