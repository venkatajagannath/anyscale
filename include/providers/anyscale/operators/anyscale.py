
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.context import Context
from custom_plugins.anyscale_hooks import AnyscaleHook
from custom_plugins.anyscale_triggers import AnyscaleJobTrigger

# Import the DeferrableOperatorMixin and TriggerRule
from airflow.models.baseoperator import BaseOperator, BaseOperatorLink
from airflow.triggers.base import BaseTrigger, TriggerEvent
from airflow.exceptions import AirflowException

import anyscale
from anyscale.sdk.anyscale_client.models import *
import logging

import logging
logging.basicConfig(level=logging.DEBUG)

class CreateAnyscaleCloud(BaseOperator):
    @apply_defaults
    def __init__(self,
                conn_id,
                cloud_config,
                xcom_push: bool = False,
                *args, **kwargs):
        super(CreateAnyscaleCloud, self).__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.cloud_config = cloud_config

    def execute(self, context):
        hook = AnyscaleHook(conn_id=self.conn_id)
        # Assuming the hook has a method create_cloud for creating an Anyscale cloud environment

        host = hook.host
        token = hook.token

        sdk = self.sdk_connection(host,token)

        result = sdk.create_cloud(self.cloud_config)

        # Pushing a dictionary to XCom
        self.xcom_push(context=context, key='AnyscaleCloud', value=result)
        logging.info("Pushed dictionary to XCom.")
        
        logging.info(f"Created Anyscale cloud with ID: {result.id}")

        return



class SubmitAnyscaleJob(BaseOperator):
    
    def __init__(self,
                 conn_id: str,
                 job_name: str,
                 cluster_env: str,
                 entrypoint: str,
                 compute_config: str = None,                 
                 runtime_env: str = None,                 
                 max_retries: int = None,
                 *args, **kwargs):
        super(SubmitAnyscaleJob, self).__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.job_name = job_name
        self.compute_config = compute_config
        self.cluster_env = cluster_env
        self.runtime_env = runtime_env
        self.entrypoint = entrypoint
        self.max_retries = max_retries

        if not self.entrypoint:
            raise AirflowException("Entrypoint is required.")
        if not self.cluster_env:
            raise AirflowException("Cluster env is required.")

    def create_compute_config(self):
        pass

    def create_cluster_env(self):
        pass

    def create_runtime_env(self):
        pass

    
    def execute(self, context: Context):
        
        sdk = AnyscaleHook(conn_id=self.conn_id)

        # Submit the job to Anyscale
        job = sdk.create_job(CreateProductionJob(
                                    name="my-production-job",
                                    description="A production job running on Anyscale.",
                                    config=None
                                ))
        self.log.info(f"Submitted Anyscale job with ID: {job_id}")
        
        # Instead of returning, defer the operator's execution using the trigger
        self.defer(trigger=AnyscaleJobTrigger(conn_id=self.conn_id, job_id=job_id), 
                   method_name="execute_complete")

    def execute_complete(self, context: Context, event: TriggerEvent) -> None:
        # This method gets called when the trigger fires that the job is complete
        self.log.info(f"Anyscale job completed with status: {event.payload['status']}")

