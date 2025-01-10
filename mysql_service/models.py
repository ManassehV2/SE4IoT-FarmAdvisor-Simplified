from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    CHAR,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class StateEnum(enum.Enum):
    Active = "Active"
    Inactive = "Inactive"
    Maintenance = "Maintenance"


class SendByEnum(enum.Enum):
    System = "System"
    User = "User"


class User(Base):
    __tablename__ = "User"
    UserID = Column(CHAR(36), primary_key=True)
    Name = Column(String(255), nullable=False)
    Phone = Column(String(255), nullable=False)
    Email = Column(String(255), nullable=False)
    AuthId = Column(String(255), nullable=False)


class Farm(Base):
    __tablename__ = "Farm"
    FarmId = Column(CHAR(36), primary_key=True)
    Name = Column(String(255), nullable=False)
    Postcode = Column(String(255), nullable=False)
    City = Column(String(255), nullable=False)
    Country = Column(String(255), nullable=False)

    fields = relationship("Field", back_populates="farm", lazy="joined")


class FarmUsers(Base):
    __tablename__ = "FarmUsers"
    UserId = Column(CHAR(36), ForeignKey("User.UserID"), primary_key=True)
    FarmId = Column(CHAR(36), ForeignKey("Farm.FarmId"), primary_key=True)
    Role = Column(Integer, nullable=False)
    Timestamp = Column(DateTime, nullable=False)

    user = relationship("User")
    farm = relationship("Farm")


class Field(Base):
    __tablename__ = "Field"
    FieldId = Column(CHAR(36), primary_key=True)
    FarmId = Column(CHAR(36), ForeignKey("Farm.FarmId"), nullable=False)
    Name = Column(String(255), nullable=False)
    Altitude = Column(Integer, nullable=False)
    Polygon = Column(Text, nullable=False)

    farm = relationship("Farm")
    sensors = relationship("Sensor", back_populates="field")


class Sensor(Base):
    __tablename__ = "Sensor"
    SensorId = Column(CHAR(36), primary_key=True)
    FieldId = Column(CHAR(36), ForeignKey("Field.FieldId"), nullable=False)
    SerialNo = Column(String(255), nullable=False)
    LastCommunication = Column(DateTime, nullable=False)
    BatterStatus = Column(Integer, nullable=False)
    OptimalGDD = Column(Integer, nullable=False)
    CuttingDateCalculated = Column(DateTime, nullable=True)
    LastForecastDate = Column(DateTime, nullable=True)
    Long = Column(Float, nullable=False)
    Lat = Column(Float, nullable=False)
    State = Column(Enum(StateEnum), nullable=False)

    field = relationship("Field", back_populates="sensors")


class SensorResetDates(Base):
    __tablename__ = "SensorResetDates"
    SensorId = Column(CHAR(36), ForeignKey(
        "Sensor.SensorId"), primary_key=True)
    Timestamp = Column(DateTime, nullable=False)
    UserId = Column(CHAR(36), ForeignKey("User.UserID"), nullable=False)

    sensor = relationship("Sensor")
    user = relationship("User")
