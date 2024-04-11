from datetime import datetime, timedelta
from airflow import DAG
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

runtime_env = RayRuntimeEnvConfig(working_dir='./ray_scripts',
                                  pip=['requests,pandas,numpy,torch'])


submit_anyscale_job = SubmitAnyscaleJob(
    task_id='submit_anyscale_job',
    auth_token = 'aph0_CkgwRgIhAMTnvzfldx9Y2O6ZButQxNnhabK9l29-tuniLuqx06w9AiEAkpipIq2s8nuS9H16vkRf5I0ZkdjSBsiPAoED24xLzM8SYxIgpnF-XZEDsT-vB9CmhIaffdz3f9FlQE1MNjuUfnPc5D8YASIedXNyX3V3Y2N3a2Z1ODN6ZXdhNXFjN2ZwYXVpYzVwOgwI6_C1kBIQqIzOngJCDAi_stWwBhCojM6eAvIBAA',
    job_name = 'AstroJob',
    build_id = 'anyscaleray2100-py39',
    entrypoint = 'python ./usr/local/airflow/dags/ray_scripts/script.py',
    compute_config_id = 'cpt_8kfdcvmckjnjqd1xwnctmpldl4',
    compute_config = None,
    runtime_env = None,
    max_retries= 5,
    dag=dag,
)


# Defining the task sequence
submit_anyscale_job
