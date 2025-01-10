# Use an official Python image as a base
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code into the container
COPY ./DataProcessor /app/

# Copy the mysql_service directory into the container
COPY ../mysql_service /app/mysql_service

# Copy the table_storage_service directory into the container
COPY ../azure_table_service /app/azure_table_service


# Copy requirements file
COPY ./DataProcessor/requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set the default command
CMD ["python", "/app/main.py"]
