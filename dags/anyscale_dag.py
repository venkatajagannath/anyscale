from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from anyscale_provider.operators.anyscale import SubmitAnyscaleJob
from pathlib import Path


def task1(params, ti, **kwargs):
    # Accessing parameters from DAG
    param1 = params["param1"]
    param2 = params["param2"]

    # Do some processing with the parameters
    result = param1 + param2

    # Passing the result to the next task
    ti.xcom_push(key="result", value=result)


# Define the DAG
dag = DAG(
    "dynamic_params_example",
    description="Example DAG showcasing passing parameters and data dynamically",
    schedule_interval=None,
    start_date=datetime(2022, 1, 1),
    catchup=False,
    params={"param1": 10, "param2": 20},
)

ANYSCALE_CONN_ID = "anyscale_conn"
FOLDER_PATH = Path(__file__).parent / "ray_scripts"

# Define the tasks
task_1 = PythonOperator(
    task_id="task1",
    python_callable=task1,
    op_kwargs={'params': dag.params},
    dag=dag
)

submit_anyscale_job = SubmitAnyscaleJob(
    task_id="submit_anyscale_job",
    conn_id=ANYSCALE_CONN_ID,
    name="AstroJob",
    image_uri="anyscale/ray:2.23.0-py311",
    compute_config="airflow-integration-testing:1",
    working_dir=str(FOLDER_PATH),
    entrypoint="python script.py --param1 {{ params.param1 }} --param2 {{ params.param2 }} --result {{ ti.xcom_pull(task_ids='task1', key='result') }}",
    requirements=["requests", "pandas", "numpy", "torch"],
    max_retries=1,
    job_timeout_seconds=3000,
    poll_interval=30,
    dag=dag,
)

# Define the task dependencies
task_1 >> submit_anyscale_job