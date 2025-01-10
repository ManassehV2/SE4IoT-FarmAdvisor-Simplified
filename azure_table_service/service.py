import logging
import random
from collections import defaultdict
from azure.data.tables import TableServiceClient, TableClient
from azure.core.exceptions import ResourceNotFoundError
from typing import List, Dict
import os
from datetime import datetime, timedelta


class AzureTableService:
    def __init__(self):
        # Fetch Azure Table Storage connection string from environment variables
        self.connection_string = os.getenv(
            'AZURE_STORAGE_SERVICE', "UseDevelopmentStorage=true")
        self.service_client = TableServiceClient.from_connection_string(
            conn_str=self.connection_string)

    def get_table_client(self, table_name: str) -> TableClient:

        return self.service_client.get_table_client(table_name)

    def create_table_if_not_exists(self, table_name: str):
        try:
            service_client = TableServiceClient.from_connection_string(
                self.connection_string)
            table_client = service_client.create_table_if_not_exists(
                table_name)
            print(f"Table '{table_name}' is ready.")
        except Exception as e:
            print(f"Error creating table '{table_name}': {str(e)}")

    def get_weather_data_with_air_temperature(self, partition_key: str = None) -> List[Dict]:

        table_name = "weatherdata"

        try:
            # Ensure the table exists (optional, but useful if the function is called prematurely)
            self.create_table_if_not_exists(table_name)

            # Get the table client
            table_client = self.get_table_client(table_name)

            # Query entities with optional PartitionKey filter
            if partition_key:
                # When filtering by PartitionKey
                query_filter = f"PartitionKey eq '{partition_key}'"
                entities = table_client.query_entities(
                    query_filter=query_filter,
                    select=["PartitionKey", "RowKey", "air_temperature"]
                )
            else:
                # When no filter is provided
                entities = table_client.query_entities(
                    query_filter="",
                    select=["PartitionKey", "RowKey", "air_temperature"]
                )

            # Convert to a list of dictionaries
            weather_data = [entity for entity in entities]

            logging.info(
                f"Retrieved {len(weather_data)} records with PartitionKey '{partition_key or 'ALL'}' from table '{table_name}'.")
            return weather_data

        except ResourceNotFoundError:
            logging.error(f"Table '{table_name}' does not exist.")
            return []
        except Exception as e:
            logging.error(
                f"Error fetching weather data from table '{table_name}': {e}")
            raise

    def get_weather_data_with_actual_temperature(self, partition_key: str = None) -> List[Dict]:

        table_name = "weatherdata"

        try:
            # Ensure the table exists (optional, but useful if the function is called prematurely)
            self.create_table_if_not_exists(table_name)

            # Get the table client
            table_client = self.get_table_client(table_name)

            # Query entities with optional PartitionKey filter
            if partition_key:
                # When filtering by PartitionKey
                query_filter = f"PartitionKey eq '{partition_key}'"
                entities = table_client.query_entities(
                    query_filter=query_filter,
                    select=["PartitionKey", "RowKey", "temperature_actual"]
                )
            else:
                # When no filter is provided
                entities = table_client.query_entities(
                    query_filter="",
                    select=["PartitionKey", "RowKey", "temperature_actual"]
                )

            # Convert to a list of dictionaries
            weather_data = [entity for entity in entities]

            logging.info(
                f"Retrieved {len(weather_data)} records with PartitionKey '{partition_key or 'ALL'}' from table '{table_name}'.")
            return weather_data

        except ResourceNotFoundError:
            logging.error(f"Table '{table_name}' does not exist.")
            return []
        except Exception as e:
            logging.error(
                f"Error fetching weather data from table '{table_name}': {e}")
            raise

    def store_entity(self, table_name, entity):

        try:
            self.create_table_if_not_exists(table_name)
            table_client = self.get_table_client(table_name)
            table_client.upsert_entity(entity)
        except Exception as e:
            print(f"Error storing entity in table '{table_name}': {e}")
            raise

    def save_weather_data_list(self, weather_data_list: List[dict]):

        table_name = "weatherdata"

        try:
            # Ensure the table exists
            self.create_table_if_not_exists(table_name)

            # Get the table client
            table_client = self.get_table_client(table_name)

            # Insert or upsert each weather data entity
            for weather_data in weather_data_list:
                table_client.upsert_entity(entity=weather_data)

            logging.info(
                f"Successfully stored {len(weather_data_list)} weather data entities in table '{table_name}'.")

        except Exception as e:
            logging.error(
                f"Error saving weather data list to table '{table_name}': {e}")
            raise

    def add_gdd_forecast(self, partition_key: str):

        try:
            # Fetch weather data with air temperature for the specified PartitionKey
            weather_data = self.get_weather_data_with_air_temperature(
                partition_key)

            logging.info(
                f"Successfully retrieved {len(weather_data)} records for PartitionKey '{partition_key}' from table 'weather'.")

            # Group data by date
            grouped_data = {}
            for record in weather_data:
                logging.info(f"Processing record: {record}")

                # Check if 'air_temperature' exists in the record
                if 'air_temperature' not in record:
                    logging.warning(
                        f"Skipping record due to missing 'air_temperature': {record}")
                    continue

                # Extract only the date from the RowKey
                date = record['RowKey'].split(" ")[0]
                logging.info(f"Record date: {date}")

                if date not in grouped_data:
                    grouped_data[date] = []
                grouped_data[date].append(record['air_temperature'])

            # Calculate the average temperature for each group
            gdd_forecast_data = []
            for date, temperatures in grouped_data.items():
                avg_temperature = sum(temperatures) / len(temperatures)
                gdd_forecast_data.append({
                    "PartitionKey": partition_key,
                    "RowKey": date,
                    "GddForecast": avg_temperature
                })

            # Insert the calculated GDD forecast into the 'GDDs' table
            table_name = "gdddata"
            self.create_table_if_not_exists(table_name)
            table_client = self.get_table_client(table_name)

            for gdd_data in gdd_forecast_data:
                table_client.upsert_entity(entity=gdd_data)

            logging.info(
                f"Successfully added {len(gdd_forecast_data)} GDD forecast records for PartitionKey '{partition_key}' to table '{table_name}'.")

        except Exception as e:
            logging.error(f"Error in add_gdd_forecast: {e}")
            raise

    def add_gdd_actual(self, partition_key: str):

        try:
            # Fetch weather data with actual temperature for the specified PartitionKey
            weather_data = self.get_weather_data_with_actual_temperature(
                partition_key)

            logging.info(
                f"Successfully retrieved {len(weather_data)} records for PartitionKey '{partition_key}' from table 'weather'.")

            # Group data by date
            grouped_data = {}
            for record in weather_data:
                logging.info(f"Processing record: {record}")

                # Check if 'air_temperature' exists in the record
                if 'temperature_actual' not in record:
                    logging.warning(
                        f"Skipping record due to missing 'temperature_actual': {record}")
                    continue

                # Extract only the date from the RowKey
                date = record['RowKey'].split(" ")[0]
                logging.info(f"Record date: {date}")

                if date not in grouped_data:
                    grouped_data[date] = []
                grouped_data[date].append(record['temperature_actual'])

            # Calculate the average temperature for each group
            gdd_actual_data = []
            for date, temperatures in grouped_data.items():
                avg_temperature = sum(temperatures) / len(temperatures)
                gdd_actual_data.append({
                    "PartitionKey": partition_key,
                    "RowKey": date,
                    "GddActual": avg_temperature
                })

            # Insert the calculated GDD forecast into the 'GDDs' table
            table_name = "gdddata"
            self.create_table_if_not_exists(table_name)
            table_client = self.get_table_client(table_name)

            for gdd_data in gdd_actual_data:
                table_client.upsert_entity(entity=gdd_data)

            logging.info(
                f"Successfully added {len(gdd_actual_data)} GDD forecast records for PartitionKey '{partition_key}' to table '{table_name}'.")

        except Exception as e:
            logging.error(f"Error in add_gdd_forecast: {e}")
            raise

    def calculate_cutting_date(self, sensor_serial_number: str, optimal_gdd: int, latest_reset_date: datetime) -> datetime:

        table_name = "gdddata"

        try:
            # Get the GDD data since the latest reset date
            self.create_table_if_not_exists(table_name)
            table_client = self.get_table_client(table_name)
            query_filter = f"PartitionKey eq '{sensor_serial_number}' and RowKey ge '{latest_reset_date.strftime('%Y-%m-%d')}'"
            entities = table_client.query_entities(query_filter=query_filter)

            # Sort the entities by date (RowKey) to ensure processing in chronological order
            gdd_data = sorted(
                [
                    {
                        "date": datetime.strptime(entity["RowKey"], "%Y-%m-%d"),
                        "gdd": entity.get("GddActual") or entity.get("GddForecast")
                    }
                    for entity in entities
                    if "GddActual" in entity or "GddForecast" in entity
                ],
                key=lambda x: x["date"]
            )

            # Accumulate GDD and determine the CuttingDateCalculated
            accumulated_gdd = 0
            for record in gdd_data:
                gdd = record["gdd"]
                if gdd is None:
                    continue  # Skip records without valid GDD values

                accumulated_gdd += gdd
                if accumulated_gdd >= optimal_gdd:
                    # CuttingDateCalculated is the date when GDD surpasses optimal_gdd
                    return record["date"]

            # If we never reach the optimal GDD, return None
            return None

        except Exception as e:
            logging.error(f"Error in calculate_cutting_date: {e}")
            raise

    def calculate_forcast_cutting_date(self, sensor_serial_number: str, optimal_gdd: int, latest_reset_date: datetime) -> datetime:

        table_name = "gdddata"

        try:
            # Get the GDD data since the latest reset date
            self.create_table_if_not_exists(table_name)
            table_client = self.get_table_client(table_name)
            query_filter = f"PartitionKey eq '{sensor_serial_number}' and RowKey ge '{latest_reset_date.strftime('%Y-%m-%d')}'"
            entities = table_client.query_entities(query_filter=query_filter)

            # Sort the entities by date (RowKey) to ensure processing in chronological order
            gdd_data = sorted(
                [
                    {
                        "date": datetime.strptime(entity["RowKey"], "%Y-%m-%d"),
                        "gdd":  entity.get("GddForecast") or 0
                    }
                    for entity in entities
                    if "GddForecast" or 0 in entity
                ],
                key=lambda x: x["date"]
            )

            # Accumulate GDD and determine the CuttingDateCalculated
            accumulated_gdd = 0
            for record in gdd_data:
                gdd = record["gdd"]
                if gdd is None:
                    continue  # Skip records without valid GDD values

                accumulated_gdd += gdd
                if accumulated_gdd >= optimal_gdd:
                    # CuttingDateCalculated is the date when GDD surpasses optimal_gdd
                    return record["date"]

            # If we never reach the optimal GDD, return None
            return None

        except Exception as e:
            logging.error(f"Error in calculate_cutting_date: {e}")
            raise

    def calculate_sensor_gdd(self, sensor_serial_number: str, latest_reset_date: datetime) -> float:

        table_name = "gdddata"

        try:
            # Get today's date in the required format
            today = datetime.now().strftime('%Y-%m-%d')

            # Get the GDD data since the latest reset date
            self.create_table_if_not_exists(table_name)
            table_client = self.get_table_client(table_name)
            query_filter = (
                f"PartitionKey eq '{sensor_serial_number}' and "
                f"RowKey ge '{latest_reset_date.strftime('%Y-%m-%d')}' and "
                f"RowKey le '{today}'"
            )
            entities = table_client.query_entities(query_filter=query_filter)

            # Sum up GDD values (prefer GddActual, fallback to GddForecast if GddActual is missing)
            cumulative_gdd = sum(
                entity.get("GddActual") or entity.get("GddForecast", 0)
                for entity in entities
            )

            logging.info(
                f"Cumulative GDD for sensor {sensor_serial_number} since {latest_reset_date}: {cumulative_gdd}")
            return cumulative_gdd

        except Exception as e:
            logging.error(
                f"Error in calculate_sensor_gdd for sensor {sensor_serial_number}: {e}")
            raise

    def get_seven_day_temperature_forecast(self, partition_key: str) -> List[Dict]:

        table_name = "weatherdata"
        try:
            self.create_table_if_not_exists(table_name)
            table_client = self.get_table_client(table_name)

            today = datetime.now().strftime('%Y-%m-%d')
            seven_days_ahead = (
                datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

            query_filter = (
                f"PartitionKey eq '{partition_key}' and "
                f"RowKey ge '{today}' and RowKey le '{seven_days_ahead}'"
            )
            entities = table_client.query_entities(
                query_filter=query_filter,
                select=["RowKey", "air_temperature"]
            )

            # Group temperatures by date
            grouped_data = defaultdict(list)
            for entity in entities:
                air_temperature = entity.get("air_temperature")
                if air_temperature is not None:  # Skip null values
                    row_date = datetime.strptime(
                        entity["RowKey"], "%Y-%m-%d %H:%M:%S").date()
                    grouped_data[row_date].append(air_temperature)

            # Calculate daily average temperature
            daily_averages = [
                {
                    "date": date,
                    # Avoid division by zero
                    "temperature": sum(temps) / len(temps) if temps else None
                }
                for date, temps in grouped_data.items()
            ]

            # Sort by date
            daily_averages.sort(key=lambda x: x["date"])
            return daily_averages

        except Exception as e:
            logging.error(
                f"Error fetching seven-day temperature forecast: {e}")
            raise

    def get_seven_day_humidity_forecast(self, partition_key: str) -> List[Dict]:

        table_name = "weatherdata"
        try:
            self.create_table_if_not_exists(table_name)
            table_client = self.get_table_client(table_name)

            today = datetime.now().strftime('%Y-%m-%d')
            seven_days_ahead = (
                datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

            query_filter = (
                f"PartitionKey eq '{partition_key}' and "
                f"RowKey ge '{today}' and RowKey le '{seven_days_ahead}'"
            )
            entities = table_client.query_entities(
                query_filter=query_filter,
                select=["RowKey", "relative_humidity"]
            )

            # Group temperatures by date
            grouped_data = defaultdict(list)
            for entity in entities:
                relative_humidity = entity.get("relative_humidity")
                if relative_humidity is not None:  # Skip null values
                    row_date = datetime.strptime(
                        entity["RowKey"], "%Y-%m-%d %H:%M:%S").date()
                    grouped_data[row_date].append(relative_humidity)

            # Calculate daily average temperature
            daily_averages = [
                {
                    "date": date,
                    # Avoid division by zero
                    "humidity": sum(temps) / len(temps) if temps else None
                }
                for date, temps in grouped_data.items()
            ]

            # Sort by date
            daily_averages.sort(key=lambda x: x["date"])
            return daily_averages

        except Exception as e:
            logging.error(
                f"Error fetching seven-day temperature forecast: {e}")
            raise

    def calculate_cumulative_gdd_forecast(self, partition_key: str, latest_reset_date: datetime) -> List[Dict]:

        table_name = "gdddata"
        try:
            # Define the forecast period
            today = datetime.now().date()  # Ensure `today` is a date object
            seven_days_ahead = today + timedelta(days=7)

            # Get the table client
            self.create_table_if_not_exists(table_name)
            table_client = self.get_table_client(table_name)

            # Query forecasted GDD data
            query_filter = (
                f"PartitionKey eq '{partition_key}' and "
                f"RowKey ge '{latest_reset_date.strftime('%Y-%m-%d')}' and "
                f"RowKey le '{seven_days_ahead.strftime('%Y-%m-%d')}'"
            )
            entities = table_client.query_entities(query_filter=query_filter)

            # Sort the forecast data by date
            forecast_data = sorted(
                [
                    {
                        # Convert to `datetime.date`
                        "date": datetime.strptime(entity["RowKey"], "%Y-%m-%d").date(),
                        # Fetch forecasted GDD
                        # entity.get("GddForecast", 0)
                        "gdd_forecast": entity.get("GddActual") or entity.get("GddForecast", 0)
                    }
                    for entity in entities
                ],
                key=lambda x: x["date"]
            )

            # Initialize cumulative GDD
            cumulative_forecast = []
            cumulative_gdd = 0

            for record in forecast_data:
                # Add GDD from reset date to current record's date
                # Normalize `latest_reset_date` to `datetime.date`
                if record["date"] >= latest_reset_date.date():
                    cumulative_gdd += record["gdd_forecast"]

                # Include only today and the next six days
                if today <= record["date"] <= seven_days_ahead:
                    cumulative_forecast.append({
                        "date": record["date"],
                        "cumulative_gdd": cumulative_gdd
                    })

            return cumulative_forecast

        except Exception as e:
            logging.error(f"Error calculating cumulative GDD forecast: {e}")
            raise
