import json
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.yandex.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocDeleteClusterOperator,
    DataprocCreatePysparkJobOperator,
)
from airflow.utils.dates import days_ago
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv('BUCKET_NAME')
SPARK_SCRIPT_PATH = os.getenv('SPARK_SCRIPT_PATH')
FOLDER_ID = os.getenv('FOLDER_ID')
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
SSH_PUBLIC_KEY = os.getenv('SSH_PUBLIC_KEY')

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )

def create_bucket():
    s3_client = get_s3_client()
    try:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        pass
    except Exception as e:
        print(f"Failed to create bucket: {e}")
        raise

def upload_to_bucket():
    s3_client = get_s3_client()
    try:
        s3_client.upload_file('/opt/airflow/spark_script.py', BUCKET_NAME, 'spark_script.py')
        s3_client.upload_file('/opt/airflow/df.json', BUCKET_NAME, 'df.json')
    except Exception as e:
        print(f"Failed to upload file: {e}")
        raise

with DAG(
    'spark_hive_yandex_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    create_bucket_task = PythonOperator(
        task_id='create_bucket',
        python_callable=create_bucket,
    )

    upload_json_task = PythonOperator(
        task_id='upload_to_bucket',
        python_callable=upload_to_bucket,
    )

    create_cluster_task = DataprocCreateClusterOperator(
        task_id='create_cluster',
        cluster_name='airflow-dataproc-cluster',
        folder_id=FOLDER_ID,
        zone='ru-central1-a',
        cluster_image_version='2.0',
        ssh_public_keys=[SSH_PUBLIC_KEY],
        services=['HDFS', 'YARN', 'SPARK', 'HIVE'],
        masternode_resource_preset='s3-c4-m16',
        masternode_disk_size=50,
        masternode_disk_type='network-ssd',
        datanode_resource_preset='s3-c4-m16',
        datanode_disk_size=50,
        datanode_disk_type='network-hdd',
        datanode_count=2,
    )

    run_pyspark_job_task = DataprocCreatePysparkJobOperator(
        task_id='run_pyspark_job',
        cluster_id="{{ task_instance.xcom_pull(task_ids='create_cluster') }}",
        main_python_file_uri=SPARK_SCRIPT_PATH,
        name='My PySpark Job',
    )

    delete_cluster_task = DataprocDeleteClusterOperator(
        task_id='delete_cluster',
        cluster_id="{{ task_instance.xcom_pull(task_ids='create_cluster') }}",
        trigger_rule='all_done',
    )

    create_bucket_task >> upload_json_task >> create_cluster_task >> run_pyspark_job_task >> delete_cluster_task
