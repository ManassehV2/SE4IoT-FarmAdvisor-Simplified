# mysql_service/service.py
import logging
from datetime import datetime
import uuid
from mysql_service.schemas import CreateFarmSchema, FarmSchema, CreateFieldSchema, CreateSensorSchema, ReadSensorSchema
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
from mysql_service.models import Base, Farm, FarmUsers, Field, Sensor, SensorResetDates, User, StateEnum
from mysql_service.config import DATABASE_CONFIG


class MySQLService:
    def __init__(self):
        self.engine = self._create_engine()
        self.Session = sessionmaker(bind=self.engine)
        # Automatically initialize the schema
        self.init_db()

    def _create_engine(self):
        """
        Create a SQLAlchemy engine.
        """
        connection_string = (
            f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
            f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
        )
        return create_engine(connection_string, echo=True)

    def get_session(self):
        """
        Provide a new SQLAlchemy session.
        """
        return self.Session()

    def init_db(self):
        """
        Initialize the database and create tables.
        """
        Base.metadata.create_all(self.engine)
        # self.seed_data()

    # CRUD Operations

    def get_all_fields(self, user: User):
        with self.get_session() as session:
            # Query fields associated with the user's farms
            fields = (
                session.query(Field)
                .join(FarmUsers, FarmUsers.FarmId == Field.FarmId)
                .filter(FarmUsers.UserId == user.UserID)
                .all()
            )
            return fields

    def create_farm(self, newfarm: CreateFarmSchema):
        with self.get_session() as db:
            newFarmmodel = Farm(
                FarmId=str(uuid.uuid4()),
                Name=newfarm.farmName,
                Postcode=newfarm.postcode,
                City=newfarm.city,
                Country=newfarm.country
            )
            db.add(newFarmmodel)
            db.commit()
            db.refresh(newFarmmodel)
            return newFarmmodel

    def create_field(self, newField: CreateFieldSchema):

        with self.get_session() as db:
            newFieldmodel = Field(
                FieldId=str(uuid.uuid4()),
                FarmId=newField.FarmId,
                Name=newField.Name,
                Altitude=newField.Altitude,
                Polygon=" ",

            )
            db.add(newFieldmodel)
            db.commit()
            db.refresh(newFieldmodel)
            return newFieldmodel

    def create_sensor(self, newSensor: CreateSensorSchema, userId: str):

        with self.get_session() as db:
            newSensormodel = Sensor(
                SensorId=str(uuid.uuid4()),
                FieldId=newSensor.FieldId,
                SerialNo=newSensor.SerialNo,
                OptimalGDD=newSensor.OptimalGDD,
                Long=newSensor.Long,
                Lat=newSensor.Lat,
                LastCommunication=datetime.now(),
                BatterStatus=1,
                State=StateEnum.Active
            )
            db.add(newSensormodel)
            db.commit()
            db.refresh(newSensormodel)

            # Create the sensor reset date entry
            sensor_reset_date = SensorResetDates(
                SensorId=newSensormodel.SensorId,
                Timestamp=datetime.now(),  # Use the current datetime
                UserId=userId
            )
            db.add(sensor_reset_date)
            db.commit()
            db.refresh(sensor_reset_date)

            return ReadSensorSchema.from_orm(newSensormodel)

    def assign_user_to_farm(self, user_id: str, farm_id: str, role: int):

        with self.get_session() as session:
            try:
                # Create a FarmUsers entry
                assignment = FarmUsers(
                    UserId=user_id,
                    FarmId=farm_id,
                    Role=role,
                    Timestamp=datetime.utcnow(),
                )
                session.add(assignment)
                session.commit()
                logging.info(
                    f"Assigned user {user_id} to farm {farm_id} with role {role}.")
            except Exception as e:
                session.rollback()
                logging.error(
                    f"Error assigning user {user_id} to farm {farm_id}: {e}")
                raise

    def get_or_create_user(self, user_info: dict):

        with self.get_session() as db:
            # Check if the user exists
            user = db.query(User).filter(
                User.AuthId == user_info.get("sub")).first()

            if not user:
                # Create a new user if not found
                user = User(
                    # Generate a new UUID for the user
                    UserID=str(uuid.uuid4()),
                    Name=user_info.get("name"),
                    Phone=user_info.get("phone", "Unknown"),
                    Email=user_info.get("email"),
                    AuthId=user_info.get("sub")
                )
            db.add(user)
            db.commit()
            db.refresh(user)

        return user

    def get_all_sensors(self):

        with self.get_session() as session:
            sensors = session.query(Sensor).all()
            return sensors

    def get_all_fields_with_sensors(self):
        with self.get_session() as session:
            # Query all fields and eagerly load their associated sensors
            fields = session.query(Field).options(
                joinedload(Field.sensors)).all()
            return fields

    def get_latest_sensor_reset_date(self, sensor_id: str):

        with self.get_session() as session:
            # Query the latest reset date for the given SensorID
            latest_reset_date = (
                session.query(SensorResetDates.Timestamp)
                .filter(SensorResetDates.SensorId == sensor_id)
                .order_by(SensorResetDates.Timestamp.desc())
                .first()
            )
            return latest_reset_date[0] if latest_reset_date else datetime.now()

    def get_latest_sensor_reset_date_by_serial(self, serial_number: str):

        with self.get_session() as session:
            # Join Sensor with SensorResetDates to get the latest reset date for the given serial number
            latest_reset_date = (
                session.query(SensorResetDates.Timestamp)
                .join(Sensor, Sensor.SensorId == SensorResetDates.SensorId)
                .filter(Sensor.SerialNo == serial_number)
                .order_by(SensorResetDates.Timestamp.desc())
                .first()
            )
            return latest_reset_date[0] if latest_reset_date else datetime.now()

    def update_sensor_cutting_date(self, serial_number: str, cutting_date: datetime):

        with self.get_session() as session:
            try:
                # Find the sensor by its serial number
                sensor = session.query(Sensor).filter(
                    Sensor.SerialNo == serial_number).first()

                if not sensor:
                    logging.warning(
                        f"Sensor with serial number {serial_number} not found.")
                    return False

                # Update the CuttingDateCalculated field
                sensor.CuttingDateCalculated = cutting_date
                session.commit()
                logging.info(
                    f"Updated CuttingDateCalculated for sensor {serial_number} to {cutting_date}.")
                return True
            except Exception as e:
                session.rollback()
                logging.error(
                    f"Error updating CuttingDateCalculated for sensor {serial_number}: {e}")
                return False

    def get_farms_with_fields_by_user(self, user_id: str):

        with self.get_session() as session:
            try:
                # Query farms associated with the user, including fields and sensors
                farms = (
                    session.query(Farm)
                    .join(FarmUsers, Farm.FarmId == FarmUsers.FarmId)
                    .filter(FarmUsers.UserId == user_id)
                    .options(joinedload(Farm.fields).joinedload(Field.sensors))
                    .all()
                )

                # Format the response
                result = []
                for farm in farms:
                    farm_data = {
                        "FarmId": farm.FarmId,
                        "Name": farm.Name,
                        "Postcode": farm.Postcode,
                        "City": farm.City,
                        "Country": farm.Country,
                        "Fields": [
                            {
                                "FieldId": field.FieldId,
                                "Name": field.Name,
                                "Altitude": field.Altitude,
                                "Polygon": field.Polygon,
                                "Sensors": [
                                    {
                                        "SensorId": sensor.SensorId,
                                        "SerialNo": sensor.SerialNo,
                                        "LastCommunication": sensor.LastCommunication,
                                        "BatterStatus": sensor.BatterStatus,
                                        "OptimalGDD": sensor.OptimalGDD,
                                        "CuttingDateCalculated": sensor.CuttingDateCalculated,
                                        "State": sensor.State.value
                                    }
                                    for sensor in field.sensors
                                ]
                            }
                            for field in farm.fields
                        ],
                    }
                    result.append(farm_data)

                return result
            except Exception as e:
                logging.error(
                    f"Error retrieving farms for user {user_id}: {e}")
                raise

    def get_field_by_id(self, field_id: str):

        with self.get_session() as session:
            field = (
                session.query(Field)
                .options(joinedload(Field.sensors))  # Eagerly load sensors
                .filter(Field.FieldId == field_id)
                .first()
            )
            return field

    def get_sensors_by_field_id(self, field_id: str):
        with self.get_session() as session:
            # Query sensors associated with the field
            sensors = session.query(Sensor).filter(
                Sensor.FieldId == field_id).all()
            return sensors

    def get_sensor_reset_date_by_sensor_id(self, sensor_id: str):

        with self.get_session() as session:
            # Query the latest reset date for the specified sensor ID
            latest_reset_date = (
                session.query(SensorResetDates.Timestamp)
                .filter(SensorResetDates.SensorId == sensor_id)
                .order_by(SensorResetDates.Timestamp.desc())
                .first()
            )
            # Return the found date or today's date if none found
            return latest_reset_date[0] if latest_reset_date else datetime.now()

    def get_latest_sensor_reset_date_by_serial(self, serial_number: str):
        with self.get_session() as session:
            # Join Sensor with SensorResetDates to get the latest reset date for the given serial number
            latest_reset_date = (
                session.query(SensorResetDates.Timestamp)
                .join(Sensor, Sensor.SensorId == SensorResetDates.SensorId)
                .filter(Sensor.SerialNo == serial_number)
                .order_by(SensorResetDates.Timestamp.desc())
                .first()
            )
            return latest_reset_date[0] if latest_reset_date else datetime.now()

    def update_or_create_sensor_reset_date(self, sensor_id: str, reset_date: datetime, user_id: str) -> bool:

        with self.get_session() as session:
            try:
                # Check if a reset date already exists for this sensor
                existing_reset_date = (
                    session.query(SensorResetDates)
                    .filter(SensorResetDates.SensorId == sensor_id)
                    .order_by(SensorResetDates.Timestamp.desc())
                    .first()
                )

                if existing_reset_date:
                    # Update the existing reset date
                    existing_reset_date.Timestamp = reset_date
                    existing_reset_date.UserId = user_id
                    logging.info(
                        f"Updated existing reset date for sensor {sensor_id} to {reset_date}.")
                else:
                    # Create a new reset date entry
                    new_reset_date = SensorResetDates(
                        SensorId=sensor_id,
                        Timestamp=reset_date,
                        UserId=user_id
                    )
                    session.add(new_reset_date)
                    logging.info(
                        f"Created new reset date for sensor {sensor_id} to {reset_date}.")

                # Commit the changes
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                logging.error(
                    f"Error updating or creating sensor reset date for sensor {sensor_id}: {e}")
                return False
