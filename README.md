## Running the Application with Docker

### step 1: Clone the Repository and Navigate to the Project Directory

1. Clone the repository using the following command: `git clone https://github.com/ManassehV2/SE4IoT-FarmAdvisor.git`

2. Navigate to the project directory: `cd SE4IoT-FarmAdvisor`

### step 2: Setup Environment Variables

Before running the project, you need to set up the environment variables. This is done by creating a `.env` file in the root directory of this project.

### Steps to Create `.env` File

1. In the root directory of the project, create a file named `.env`.
2. Add the following content to the `.env` file:

   ```env
   DB_HOST=mysql_db
   DB_PORT=3306
   DB_NAME=farmadvisor
   DB_USER=root
   DB_PASSWORD=password01
   STORAGE_SERVICE="DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;TableEndpoint=http://azurite:10002/devstoreaccount1;"
   BLOB_STORAGE_SERVICE="DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://azurite:10000/devstoreaccount1;"
   KAFKA_TOPIC="sensor_data"
   AUTH0_DOMAIN=dev-7q1hcma4yuzy68dc.us.auth0.com
   AUTH0_CLIENT_ID=lzEduAYKdEE4UH2IQudBZwBgfc8MhQvi
   AUTH0_AUDIENCE=http://localhost:8000
   BASE_WEATHER_API_URL=https://api.met.no/weatherapi/locationforecast/2.0
   MQTT_USER=user1
   MQTT_PASSWORD=password01
   CRON_SCHEDULE=0 * * * * *
   DATA_GENERATION_INTERVAL_SEC=120
   ```

3. Save the file.

   Explanation of Key Environment Variables:

   #### Database Configuration:

   - **`DB_HOST`**: Hostname or IP address of the MySQL database.
   - **`DB_PORT`**: Port on which the MySQL database is running (default is `3306`).
   - **`DB_NAME`**: Name of the database to use.
   - **`DB_USER`**: Username for accessing the database.
   - **`DB_PASSWORD`**: Password for accessing the database.

   #### Azure Storage Configuration:

   - **`STORAGE_SERVICE`**: Connection string for Azure Table Storage.
   - **`BLOB_STORAGE_SERVICE`**: Connection string for Azure Blob Storage.

   #### Kafka Configuration:

   - **`KAFKA_TOPIC`**: Name of the Kafka topic to which the application publishes and subscribes.

   #### Auth0 Configuration:

   - **`AUTH0_DOMAIN`**: The domain for the Auth0 tenant (used for authentication).
   - **`AUTH0_CLIENT_ID`**: Client ID for the Auth0 application.
   - **`AUTH0_AUDIENCE`**: Audience URI for the API being secured with Auth0.

   #### Weather API Configuration:

   - **`BASE_WEATHER_API_URL`**: URL for the MET Weather API, used for fetching weather forecasts.

   #### MQTT Broker Configuration:

   - **`MQTT_USER`**: Username for authenticating with the MQTT broker.
   - **`MQTT_PASSWORD`**: Password for authenticating with the MQTT broker.

   #### Task Scheduling:

   - **`CRON_SCHEDULE`**: Cron expression used to schedule tasks in the application.
   - **`DATA_GENERATION_INTERVAL_SEC`**: Interval (in seconds) for generating data during simulation.

### Step 3: Give execution permission for the setup-kafka-connect.sh

In the root directory of the project there is a file named `setup-kafka-connect.sh` inside the `scripts` directory. This script configures Kafka Connect to use the MQTT Source Connector. It installs the MQTT plugin, starts Kafka Connect, injects MQTT credentials, and deploys the connector.

Ensure the script has execution permissions by running the following command in the terminal before building the application:

`chmod +x ./scripts/setup-kafka-connect.sh`

### Step 4: Build and Run the Containers

Use Docker Compose to build and run all the services defiend in the `docker-compose.yml`.

`docker compose up --build`

### Step 5: Accessing the Application and Services

1. **API Service**:

   - The backend API is available at `http://localhost:8000`.
   - Swagger documentation for the API is available at `http://localhost:8000/docs`.

2. **Angular Dashboard**:
   - Access the front-end application at `http://localhost:8080`.

### Step 6: Stopping the Containers

To stop the running containers, use:

`docker compose down`

## System Architecture

Below is the system architecture of the application:

![System Architecture](./System_Architecture.png)

## Demo Video 

🔗 [Demo video](https://drive.google.com/file/d/1q_oWiyis_RrzCsmatNgscPXRivqp7pZG/view?usp=share_link)
