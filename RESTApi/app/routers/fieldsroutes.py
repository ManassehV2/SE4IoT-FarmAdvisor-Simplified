import logging
import math
from fastapi import HTTPException
from azure_table_service.service import AzureTableService
from fastapi import FastAPI, Depends
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from mysql_service import MySQLService
from uuid import UUID

import os
from mysql_service.schemas import FieldDashboardSchema, FieldSensorSchema, GraphData, ReadFieldSchema, CreateFieldSchema, CreateSensorSchema, ReadSensorSchema, UpdateSensorResetDateSchema
from app.auth.auth import get_current_user
from mysql_service.dependencies import get_mysql_service
from azure_table_service.dependencies import get_azure_table_service

router = APIRouter(
    prefix="/fields",
    tags=["fields"],
)


@router.get("/fielddashboard{field_id}", response_model=FieldDashboardSchema)
def read_farm_dashboard(
        field_id: UUID,
        current_user: dict = Depends(get_current_user),
        mysql_service: MySQLService = Depends(get_mysql_service),
        table_service: AzureTableService = Depends(get_azure_table_service)):

    try:
        # 1. Retrieve field details using MySQLService
        field = mysql_service.get_field_by_id(str(field_id))
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")

        # 2. Extract field-level data
        field_name = field.Name
        altitude = field.Altitude

        # 3. Retrieve sensors (already eagerly loaded)
        sensors = field.sensors
        if not sensors:
            return FieldDashboardSchema(
                FieldName=field_name,
                Altitude=altitude,
                FieldSensors=[],
            )

        # 4. Select the first sensor and calculate GDD forecast
        selected_sensor = sensors[0]
        latest_reset_date = mysql_service.get_latest_sensor_reset_date_by_serial(
            selected_sensor.SerialNo)
        gdd_forecast = table_service.calculate_cumulative_gdd_forecast(
            partition_key=selected_sensor.SerialNo,
            latest_reset_date=latest_reset_date
        )

        # 5. Convert GDD forecast to GraphData format
        seven_day_gdd_forecast = [
            GraphData(date=record["date"], value=record["cumulative_gdd"]) for record in gdd_forecast
        ]

        # 6. Fetch seven-day temperature forecast
        temperature_forecast = table_service.get_seven_day_temperature_forecast(
            partition_key=selected_sensor.SerialNo
        )
        seven_day_temp_forecast = [
            GraphData(date=record["date"], value=record["temperature"]) for record in temperature_forecast
        ]
        humidity_forecast = table_service.get_seven_day_humidity_forecast(
            partition_key=selected_sensor.SerialNo)

        seven_day_humidity_forecast = [
            GraphData(date=record["date"], value=record["humidity"]) for record in humidity_forecast

        ]

        # 7. Prepare the response
        response = FieldDashboardSchema(
            FieldName=field_name,
            Altitude=altitude,
            CurrentGDD=math.ceil(table_service.calculate_sensor_gdd(
                sensors[0].SerialNo, latest_reset_date)),
            OptimalGDD=selected_sensor.OptimalGDD,
            # table_service.calculate_forcast_cutting_date(
            CuttingDateCalculated=sensors[0].CuttingDateCalculated,
            # selected_sensor.SerialNo, selected_sensor.OptimalGDD, latest_reset_date),  #
            FieldSensors=[
                {
                    "SensorId": sensor.SensorId,
                    "SerialNo": sensor.SerialNo,
                    "OptimalGDD": sensor.OptimalGDD,
                    "SensorResetDate": mysql_service.get_sensor_reset_date_by_sensor_id(sensor.SensorId),
                    "State": sensor.State.value,
                } for sensor in sensors
            ],
            SevenDayTempForecast=seven_day_temp_forecast,  # Add temperature forecast
            SevenDayGDDForecast=seven_day_gdd_forecast,
            SevenDayHumidityForecast=seven_day_humidity_forecast
        )
        return response

    except Exception as e:
        logging.error(f"Error retrieving field dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/newfield", response_model=ReadFieldSchema)
def create_field(
        new_field: CreateFieldSchema,
        current_user: dict = Depends(get_current_user),
        mysql_service: MySQLService = Depends(get_mysql_service)):

    # Create the field
    created_field = mysql_service.create_field(new_field)

    return created_field


@router.post("/newsensor", response_model=ReadSensorSchema)
def create_field(
        new_sensor: CreateSensorSchema,
        current_user: dict = Depends(get_current_user),
        mysql_service: MySQLService = Depends(get_mysql_service)):

    user = mysql_service.get_or_create_user(current_user)
    # Create the sensor
    created_sensor = mysql_service.create_sensor(new_sensor, user.UserID)

    return created_sensor


@router.put("/sensor/resetdate", response_model=bool)
def update_sensor_reset_date(
        update_data: UpdateSensorResetDateSchema,
        current_user: dict = Depends(get_current_user),
        mysql_service: MySQLService = Depends(get_mysql_service)):

    try:
        user = mysql_service.get_or_create_user(current_user)
        # Call the MySQL service to update the reset date
        success = mysql_service.update_or_create_sensor_reset_date(
            sensor_id=str(update_data.SensorId),
            reset_date=update_data.NewResetDate,
            user_id=user.UserID
        )
        if not success:
            raise HTTPException(
                status_code=404, detail="Sensor not found or update failed")
        return success
    except Exception as e:
        logging.error(f"Error updating sensor reset date: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
