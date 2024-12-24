FROM apache/airflow:slim-2.8.0-python3.8


USER root


RUN apt-get update && apt-get install -y \
    curl \
    nano \
    tini \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


USER airflow


ENV PYTHONPATH=/opt/airflow


COPY requirements.txt /requirements.txt


RUN /usr/local/bin/python3 -m pip install --no-cache-dir -r /requirements.txt && \
    pip install --no-cache-dir python-dotenv


COPY .env /opt/airflow/.env


ENV AIRFLOW_HOME=/opt/airflow \
    AIRFLOW_UID=${AIRFLOW_UID} \
    AIRFLOW_GID=${AIRFLOW_GID} \
    FOLDER_ID=${FOLDER_ID} \
    ACCESS_KEY=${ACCESS_KEY} \
    SECRET_KEY=${SECRET_KEY} \
    BUCKET_NAME=${BUCKET_NAME} \
    SPARK_SCRIPT_PATH=${SPARK_SCRIPT_PATH} \
    SSH_PUBLIC_KEY=${SSH_PUBLIC_KEY} \
    FERNET_KEY=${FERNET_KEY}


COPY dags /opt/airflow/dags



ENTRYPOINT ["tini", "--", "/entrypoint"]