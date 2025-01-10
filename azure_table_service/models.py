# models.py
class SensorDataModel:
    def __init__(self, partition_key: str, row_key: str, timestamp: str, temperature: float, humidity: float, pressure: float):
        self.partition_key = partition_key
        self.row_key = row_key
        self.timestamp = timestamp
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure

    def to_dict(self):
        """
        Convert the model to a dictionary for Table Storage.
        """
        return {
            "PartitionKey": self.partition_key,
            "RowKey": self.row_key,
            "Timestamp": self.timestamp,
            "Temperature": self.temperature,
            "Humidity": self.humidity,
            "Pressure": self.pressure,
        }
