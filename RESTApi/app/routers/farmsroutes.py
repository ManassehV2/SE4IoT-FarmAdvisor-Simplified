import logging
import math
from azure_table_service.service import AzureTableService
from fastapi import FastAPI, Depends
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from mysql_service import MySQLService


import os
from mysql_service.schemas import CreateFarmSchema, FarmDashboardSchema, FieldDetail, ReadFarmSchema
from app.auth.auth import get_current_user
from mysql_service.dependencies import get_mysql_service
from azure_table_service.dependencies import get_azure_table_service

router = APIRouter(
    prefix="/farms",
    tags=["farms"],
)


@router.get("/farmdashboard", response_model=list[FarmDashboardSchema])
def read_farm_dashboard(
        current_user: dict = Depends(get_current_user),
        mysql_service: MySQLService = Depends(get_mysql_service),
        table_service: AzureTableService = Depends(get_azure_table_service)):

    # Log user info
    print("Current User:", current_user)

    # Fetch user and their farms with fields
    user = mysql_service.get_or_create_user(current_user)
    farms_with_fields = mysql_service.get_farms_with_fields_by_user(
        user.UserID)

    # Map to FarmDashboardSchema
    response = []
    for farm in farms_with_fields:
        farm_fields = []
        for field in farm["Fields"]:
            gdd_values = []
            cutting_dates = []
            for sensor in field["Sensors"]:
                # Get the latest reset date
                latest_reset_date = mysql_service.get_latest_sensor_reset_date(
                    sensor["SensorId"])

                # Calculate the cumulative GDD for the sensor
                gdd = table_service.calculate_sensor_gdd(
                    sensor["SerialNo"], latest_reset_date)
                gdd_values.append(gdd)

                # Use the pre-calculated cutting date
                if sensor["CuttingDateCalculated"]:
                    cutting_dates.append(sensor["CuttingDateCalculated"])

            # Compute average GDD for the field
            current_gdd = math.ceil(
                sum(gdd_values) / len(gdd_values)) if gdd_values else 0

            # Determine the earliest cutting date for the field
            optimal_cutting_date = min(
                cutting_dates) if cutting_dates else None

            # Create FieldDetail object
            field_detail = FieldDetail(
                FieldId=field["FieldId"],
                FieldName=field["Name"],
                CurrentGDD=current_gdd,
                OptimalCuttingDate=optimal_cutting_date
            )
            farm_fields.append(field_detail)

        # Create FarmDashboardSchema object
        farm_dashboard = FarmDashboardSchema(
            FarmId=farm["FarmId"],
            FarmName=farm["Name"],
            FarmFields=farm_fields
        )
        response.append(farm_dashboard)

    return response


@router.post("/newfarm", response_model=ReadFarmSchema)
def create_farm(
        new_farm: CreateFarmSchema,
        current_user: dict = Depends(get_current_user),
        mysql_service: MySQLService = Depends(get_mysql_service)):

    # Fetch the current user
    user = mysql_service.get_or_create_user(current_user)

    # Create the farm
    created_farm = mysql_service.create_farm(new_farm)

    mysql_service.assign_user_to_farm(
        user.UserID, created_farm.FarmId, role=1)

    return created_farm
