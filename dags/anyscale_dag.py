from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
# Assuming these hooks and operators are custom or provided by a plugin
from providers.anyscale.operators.anyscale import SubmitAnyscaleJob
from providers.anyscale.hooks.anyscale import AnyscaleHook
from providers.anyscale.models.CreateProductionJobConfig import RayRuntimeEnvConfig,JobConfiguration

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 2),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'anyscale_workflow',
    default_args=default_args,
    description='A DAG to interact with Anyscale triggered manually',
    schedule_interval=None,  # This DAG is not scheduled, only triggered manually
    catchup=False,
)

runtime_env = RayRuntimeEnvConfig(working_dir='./',
                                  pip=['requests,pandas,numpy,torch'])


submit_anyscale_job = SubmitAnyscaleJob(
    task_id='submit_anyscale_job',
    conn_id= "",
    job_name="Basic ray job",
    build_id='',
    entrypoint='python script.py',
    compute_config_id='',
    runtime_env= runtime_env,
    max_retries=10,
    dag=dag,
)


# Defining the task sequence
submit_anyscale_job
