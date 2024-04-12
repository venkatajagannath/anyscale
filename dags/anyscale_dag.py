from datetime import datetime, timedelta
from airflow import DAG
import os
# Assuming these hooks and operators are custom or provided by a plugin
from providers.anyscale.operators.anyscale import SubmitAnyscaleJob
from providers.anyscale.hooks.anyscale import AnyscaleHook
from providers.anyscale.models.CreateProductionJobConfig import RayRuntimeEnvConfig,JobConfiguration

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

# Define the AWS connection
conn = Connection(
    conn_id="aws_conn",
    conn_type="aws",
    extra={
        "config_kwargs": {
            "signature_version": "unsigned",
        },
    },
)

# Constants
BUCKET_NAME = 'anyscale-production-data-cld-g7m5cn8nnhkydikcjc6lj4ekye/'
FOLDER_PATH = './ray_scripts'
AWS_CONN_ID = 'aws_conn'

dag = DAG(
    'anyscale_workflow',
    default_args=default_args,
    description='A DAG to interact with Anyscale triggered manually',
    schedule_interval=None,  # This DAG is not scheduled, only triggered manually
    catchup=False,
)

runtime_env = RayRuntimeEnvConfig(working_dir='s3://anyscale-production-data-cld-g7m5cn8nnhkydikcjc6lj4ekye/scripts/',
                                  pip=['requests,pandas,numpy,torch'])

def list_files():
    """ Generate a list of files to be uploaded """
    for root, dirs, files in os.walk(FOLDER_PATH):
        for file in files:
            yield os.path.join(root, file)


# Dynamically create tasks for each file
for file_path in list_files():
    filename = file_path[len(FOLDER_PATH):].lstrip(os.sep)
    s3_key = os.path.join('scripts', filename)
    
    upload_task = LocalFilesystemToS3Operator(
        task_id=f'upload_{filename.replace(os.sep, "_")}',  # Create a valid task id
        filename=file_path,
        dest_key=s3_key,
        dest_bucket=BUCKET_NAME,
        aws_conn_id=AWS_CONN_ID,
        replace=True,
        dag=dag
    )


submit_anyscale_job = SubmitAnyscaleJob(
    task_id='submit_anyscale_job',
    auth_token = 'aph0_CkgwRgIhAMTnvzfldx9Y2O6ZButQxNnhabK9l29-tuniLuqx06w9AiEAkpipIq2s8nuS9H16vkRf5I0ZkdjSBsiPAoED24xLzM8SYxIgpnF-XZEDsT-vB9CmhIaffdz3f9FlQE1MNjuUfnPc5D8YASIedXNyX3V3Y2N3a2Z1ODN6ZXdhNXFjN2ZwYXVpYzVwOgwI6_C1kBIQqIzOngJCDAi_stWwBhCojM6eAvIBAA',
    job_name = 'AstroJob',
    build_id = 'anyscaleray2100-py39',
    entrypoint = 'python script.py',
    compute_config_id = 'cpt_8kfdcvmckjnjqd1xwnctmpldl4',
    compute_config = None,
    runtime_env = runtime_env,
    max_retries= 2,
    dag=dag,
)


# Defining the task sequence
submit_anyscale_job
