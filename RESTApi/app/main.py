from azure_table_service.service import AzureTableService
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from mysql_service import MySQLService

import os
from mysql_service.schemas import CreateFarmSchema
from app.auth.auth import get_current_user
from mysql_service.dependencies import get_mysql_service
from azure_table_service.dependencies import get_azure_table_service
from .routers import farmsroutes, fieldsroutes

# Create FastAPI app
app = FastAPI(
    title="GDD Rest API",
    version="1.0.0",
    contact={
        "name": "Minase Mengistu",
        "email": "minase.mengistu@abo.fi",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Include the routers
app.include_router(farmsroutes.router)
app.include_router(fieldsroutes.router)
