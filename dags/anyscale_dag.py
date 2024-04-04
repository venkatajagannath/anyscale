from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
# Assuming these hooks and operators are custom or provided by a plugin
from providers.anyscale.operators.anyscale import CreateAnyscaleCloud, SubmitAnyscaleJob
from providers.anyscale.hooks.anyscale import AnyscaleHook

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

start = DummyOperator(
    task_id='start',
    dag=dag,
)

create_anyscale_cloud = CreateAnyscaleCloud(
    task_id='create_anyscale_cloud',
    conn_id='anyscale',  # Connection ID to use
    cloud_config={'region': 'us-west-2'},  # Example config, adjust as needed
    dag=dag,
)

submit_anyscale_job = SubmitAnyscaleJob(
    task_id='submit_anyscale_job',
    job_name= "123",
    cluster_env= "234",
    entrypoint='python script.py',
    dag=dag,
)

end = DummyOperator(
    task_id='end',
    dag=dag,
)

# Defining the task sequence
start >> create_anyscale_cloud >> submit_anyscale_job >> end
