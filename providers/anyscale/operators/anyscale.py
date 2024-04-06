
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.context import Context
from providers.anyscale.hooks.anyscale import AnyscaleHook
from providers.anyscale.triggers.anyscale import AnyscaleJobTrigger

# Import the DeferrableOperatorMixin and TriggerRule
from airflow.models.baseoperator import BaseOperator, BaseOperatorLink
from airflow.triggers.base import BaseTrigger, TriggerEvent
from airflow.exceptions import AirflowException

import anyscale
from anyscale.sdk.anyscale_client.models import *
import logging

import logging
logging.basicConfig(level=logging.DEBUG)

"""class CreateAnyscaleCloud(BaseOperator):
    
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

        return"""



class SubmitAnyscaleJob(BaseOperator):
    
    def __init__(self,
                 conn_id: str,
                 job_name: str,
                 build_id: str,
                 entrypoint: str,
                 compute_config_id: str = None,
                 compute_config: dict = None,                 
                 runtime_env: str = None,                 
                 max_retries: int = None,
                 *args, **kwargs):
        super(SubmitAnyscaleJob, self).__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.job_name = job_name
        self.build_id = build_id
        self.runtime_env = runtime_env
        self.entrypoint = entrypoint
        self.compute_config_id = compute_config_id
        self.compute_config = compute_config
        self.max_retries = max_retries

        if not self.entrypoint:
            raise AirflowException("Entrypoint is required.")
        if not self.job_name:
            raise AirflowException("Cluster env is required.")

    
    def execute(self, context: Context):
        
        sdk = AnyscaleHook(conn_id=self.conn_id)

        job_config = CreateProductionJobConfig(entrypoint = self.entrypoint,
                                               runtime_env = self.runtime_env,
                                               build_id = self.build_id,
                                               compute_config_id = self.compute_config_id,
                                               compute_config = self.compute_config,
                                               max_retries = self.max_retries)

        # Submit the job to Anyscale
        prod_job : ProductionjobResponse = sdk.create_job(CreateProductionJob(
                                    name=self.job_name,
                                    config=job_config))
        
        self.log.info(f"Submitted Anyscale job with ID: {prod_job.result.id}")
        
        # Instead of returning, defer the operator's execution using the trigger
        self.defer(trigger=AnyscaleJobTrigger(conn_id=self.conn_id, job_id=prod_job.result.id), 
                   method_name="execute_complete")

    def execute_complete(self, context: Context, event: TriggerEvent) -> None:
        # This method gets called when the trigger fires that the job is complete
        self.log.info(f"Anyscale job completed with status: {event.payload['status']}")

