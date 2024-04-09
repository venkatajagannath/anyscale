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
    auth_token = 'aph0_CkYwRAIgYZCgy_uLwcNj6hs0lR9pBJHuXNNS_EnMNRUuex0E8LYCIB6uM7IN1fZ94Xcow9oq-4IcQfNVxyTjT9jglrG7pC6pEmESIKcVEKk-rzB5180goqh95e6cXOnhuiqlaLNC73APutT0GAEiHnVzcl91d2Njd2tmdTgzemV3YTVxYzdmcGF1aWM1cDoLCNG_spASEPjssyRCCwilgdKwBhD47LMk8gEA',
    job_name = 'AstroJob',
    build_id = 'ses_95yuixd4xs8k5ns7euf2izif1d',
    entrypoint = 'python ./script.py',
    compute_config_id = 'cpt_wbkzkfzfjpngn71bcgp1mvdcsa',
    compute_config = None,
    runtime_env = runtime_env.to_dict,
    max_retries= 5,
    dag=dag,
)


# Defining the task sequence
submit_anyscale_job
