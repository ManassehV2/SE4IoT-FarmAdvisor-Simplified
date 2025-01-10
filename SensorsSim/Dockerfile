# Use an official Python image as a base
FROM python:3.8-slim

# Set the working directory
WORKDIR /app


# Copy necessary files
COPY ./SensorsSim /app/

# Copy the mysql_service directory into the container
COPY ../mysql_service  /app/mysql_service

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set the default command
CMD ["python", "/app/sensor_simulator.py"]

