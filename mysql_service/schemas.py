# mysql_service/schemas.py

from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from typing import Optional, List


class StateEnum(str, Enum):
    Active = "Active"
    Inactive = "Inactive"
    Maintenance = "Maintenance"


class SendByEnum(str, Enum):
    System = "System"
    User = "User"


class UserSchema(BaseModel):
    UserID: str
    Name: str
    Phone: str
    Email: str
    AuthId: str

    class Config:
        orm_mode = True


class FarmSchema(BaseModel):
    FarmId: str
    Name: str
    Postcode: str
    City: str
    Country: str

    class Config:
        orm_mode = True


class CreateFarmSchema(BaseModel):
    farmName: str
    postcode: str
    city: str
    country: str

    class Config:
        orm_mode = True


class ReadFarmSchema(BaseModel):
    FarmId: str
    Name: str
    Postcode: str
    City: str
    Country: str

    class Config:
        orm_mode = True


class FarmUsersSchema(BaseModel):
    UserId: str
    FarmId: str
    Role: int
    Timestamp: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True


class CreateFieldSchema(BaseModel):
    FarmId: str
    Name: str
    Altitude: int

    class Config:
        orm_mode = True


class ReadFieldSchema(BaseModel):
    FieldId: str
    FarmId: str
    Name: str
    Altitude: int

    class Config:
        orm_mode = True


class CreateSensorSchema(BaseModel):
    FieldId: str
    SerialNo: str
    OptimalGDD: int
    Long: float
    Lat: float

    class Config:
        orm_mode = True


class ReadSensorSchema(BaseModel):
    SensorId: str
    FieldId: str
    SerialNo: str
    LastCommunication: Optional[datetime] = None
    BatterStatus: Optional[int] = None
    OptimalGDD: int
    CuttingDateCalculated: Optional[datetime] = None
    LastForecastDate: Optional[datetime] = None
    Long: float
    Lat: float
    State: StateEnum

    class Config:
        orm_mode = True
        from_attributes = True


class SensorResetDatesSchema(BaseModel):
    SensorId: str
    Timestamp: datetime
    UserId: str

    class Config:
        orm_mode = True


class FieldDetail(BaseModel):
    FieldId: str
    FieldName: str
    CurrentGDD: float
    OptimalCuttingDate: Optional[datetime]


class FarmDashboardSchema(BaseModel):
    FarmId: str
    FarmName: str
    FarmFields: List[FieldDetail] = []


class FieldSensorSchema(BaseModel):
    SensorId: str
    SerialNo: str
    OptimalGDD: float
    SensorResetDate: datetime
    State: str


class GraphData(BaseModel):
    date: datetime
    value: float


class FieldDashboardSchema(BaseModel):
    FieldName: str
    Altitude: int
    CurrentGDD: Optional[float] = None
    OptimalGDD: Optional[float] = None
    CuttingDateCalculated: Optional[datetime] = None
    FieldSensors: List[FieldSensorSchema] = []
    SevenDayTempForecast: List[GraphData] = []
    SevenDayGDDForecast: List[GraphData] = []
    SevenDayHumidityForecast: List[GraphData] = []


class UpdateSensorResetDateSchema(BaseModel):
    SensorId: str
    NewResetDate: datetime
