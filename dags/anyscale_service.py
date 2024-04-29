from datetime import datetime, timedelta
from airflow import DAG
import os
# Assuming these hooks and operators are custom or provided by a plugin
from include.operators.anyscale import SubmitAnyscaleJob, RolloutAnyscaleService
from include.hooks.anyscale import AnyscaleHook
from include.models.CreateProductionJobConfig import RayRuntimeEnvConfig,JobConfiguration

from datetime import datetime, timedelta

from airflow.models.connection import Connection
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
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
    build_id="bld_7qsgb3mnjp7juibl6jetl9lhbu",
    compute_config_id="cpt_8kfdcvmckjnjqd1xwnctmpldl4",
    ray_serve_config={ 
        "applications": [
            {
                "name": "sentiment_analysis",
                "runtime_env": {
                    "working_dir": "https://github.com/anyscale/docs_examples/archive/refs/heads/main.zip"
                },
                "import_path": "sentiment_analysis.app:model",
            }
        ]
    },
    version = 10,
    canary_percent = 50,
    dag=dag
)


# Defining the task sequence
deploy_anyscale_service
