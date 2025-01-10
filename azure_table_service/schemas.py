# schemas.py
from pydantic import BaseModel, Field
from datetime import datetime

class SensorDataSchema(BaseModel):
    PartitionKey: str
    RowKey: str
    Timestamp: datetime
    Temperature: float
    Humidity: float
    Pressure: float

    class Config:
        orm_mode = True
