# Use an official Python image
FROM python:3.9-slim

# Install curl
RUN apt-get update && apt-get install -y curl && apt-get clean

# Set work directory
WORKDIR /app

# Copy application code
COPY ./RESTApi /app

# Copy the mysql_service directory into the container
COPY ../mysql_service /app/mysql_service

# Copy the table_storage_service directory into the container
COPY ../azure_table_service /app/azure_table_service

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
