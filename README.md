# Spark Hive Yandex Data Pipeline with Airflow and Docker Compose

This project uses **Docker Compose** to manage an Airflow environment orchestrating a pipeline with Yandex Cloud. The pipeline involves uploading files to Yandex Object Storage, creating a Dataproc cluster, running a PySpark job, and performing data transformations using Spark and Hive.

## What has been done

1. **Docker Compose Setup**:
   - docker-compose.yml` file to set up services for **Airflow** and a **PostgreSQL** database, along with the necessary configuration for Yandex Cloud pipeline.
   - Airflow uses a **LocalExecutor** to run DAGs, stores metadata in a PostgreSQL database, and loads environment variables from `.env` to manage sensitive credentials.
   - The environment variables include Yandex Cloud credentials, Airflow configurations, and paths to the necessary files (like the Spark script, JSON data, and SSH public key).

2. **Airflow Configuration**:
   - The `docker-compose.yml` file defines several Airflow services:
     - **airflow-webserver**: Web interface for Airflow.
     - **airflow-scheduler**: Responsible for scheduling DAGs.
     - **airflow-init**: Initializes the Airflow environment (e.g., creates the default admin user and upgrades the database).
   - Each service has a `healthcheck` to ensure that they are running properly.
   - The **PostgreSQL database** is used to store Airflow's metadata and is connected to all Airflow components.
   - **Volumes** are mapped to persist logs, data, and configuration files.

3. **Environment Configuration**:
   - The `.env` file stores the sensitive configuration variables for the project, such as Yandex Cloud keys, Airflow settings, and paths.
   - The **SSH_PUBLIC_KEY** is used for authentication with Yandex Cloud.

4. **Airflow DAG**:
   - A **DAG** is defined to automate the process of:
     - Creating a Yandex Object Storage bucket.
     - Uploading Spark script and data files.
     - Creating a Yandex Dataproc cluster.
     - Running the PySpark job.
     - Deleting the cluster after job completion.

5. **PySpark Script**:
   - The **PySpark script** reads JSON data from Yandex Object Storage, processes it with Spark, writes the data to Hive, and saves the transformed data back to Yandex Object Storage.

## How to Use

1. **Set Up the Environment**:
   - Ensure your `.env` file is correctly configured with the necessary credentials and paths:
     ```env
     AIRFLOW_UID=1000
     AIRFLOW_GID=0

     FERNET_KEY=your_fernet_key
     ACCESS_KEY=your_access_key
     SECRET_KEY=your_secret_key
     BUCKET_NAME=your_bucket_name
     SPARK_SCRIPT_PATH=s3://your-bucket/spark_script.py
     SSH_PUBLIC_KEY=path/to/your/ssh_public_key
     FOLDER_ID=your_folder_id

     _AIRFLOW_WWW_USER_USERNAME=airflow
     _AIRFLOW_WWW_USER_PASSWORD=airflow
     ```

2. **Build and Start Docker Compose**:
   - From the project directory, build and start the containers:
     ```bash
     docker-compose up --build
     ```
   - This will set up all the necessary services, including Airflow, PostgreSQL, and your environment.

3. **Access Airflow UI**:
   - Once the containers are up, you can access the Airflow web interface at `http://localhost:8080`.
   - Log in using the username and password specified in the `.env` file (default: `airflow`/`airflow`).
   - Set your connection for Yandex Cloud and fill required options, like Service account auth JSON or OAuth token 
   (connection_Id =conyandexcloud_default)

4. **Run the DAG**:
   - In the Airflow UI, trigger the DAG `spark_hive_yandex_dag` to start the process of creating the Yandex Cloud bucket, uploading files, creating the Dataproc cluster, running the PySpark job, and performing data transformations.
   By default, set to be triggered manually

5. **Monitor the Pipeline**:
   - You can monitor the progress of the DAG and check logs for each task directly from the Airflow UI.

## Summary

This project leverages **Docker Compose** to run an **Airflow** setup that orchestrates a **Yandex Cloud Dataproc** pipeline. The pipeline automates the process of data storage, processing with Spark, and transformation with Hive, using environment variables for secure management of credentials and configurations. All services are configured in the `docker-compose.yml` file, which makes it easy to deploy and manage the pipeline locally or on a server.
