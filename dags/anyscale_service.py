
from datetime import datetime, timedelta
from airflow import DAG
import os

from include.operators.anyscale import RolloutAnyscaleService

from airflow.models.connection import Connection
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 2),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the Anyscale connection
ANYSCALE_CONN_ID = "anyscale_conn"

dag = DAG(
    'anyscale_service_workflow',
    default_args=default_args,
    description='A DAG to interact with Anyscale triggered manually',
    schedule_interval=None,  # This DAG is not scheduled, only triggered manually
    catchup=False,
)

deploy_anyscale_service = RolloutAnyscaleService(
    task_id="rollout_anyscale_service",
    conn_id = ANYSCALE_CONN_ID,
    name="AstroService",
    image_uri = 'bld_7qsgb3mnjp7juibl6jetl9lhbu',
    compute_config = 'cld_g7m5cn8nnhkydikcjc6lj4ekye',
    working_dir = "https://github.com/anyscale/docs_examples/archive/refs/heads/main.zip",
    applications = [
        {"import_path": "sentiment_analysis.app:model"}
    ],
    in_place=True,
    canary_percent= 50,
    dag=dag
)

# Defining the task sequence
deploy_anyscale_service
