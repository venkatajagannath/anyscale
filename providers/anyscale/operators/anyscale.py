
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
from anyscale import AnyscaleSDK
from airflow.utils.context import Context

from typing import Optional
from airflow.models.baseoperator import BaseOperator
from airflow.compat.functools import cached_property
from anyscale.sdk.anyscale_client.models import *
import logging

import logging
logging.basicConfig(level=logging.DEBUG)

class AnyscaleBaseOperator():
    def __init__(
        self,
        *,
        auth_token: str,
        poke_interval: Optional[int] = 60,
        **kwargs
    ):
        self.auth_token = auth_token
        self.poke_interval = poke_interval
        super().__init__(**kwargs)

    @cached_property
    def sdk(self) -> AnyscaleSDK:
        return AnyscaleSDK(auth_token=self.auth_token)

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



class SubmitAnyscaleJob(BaseOperator,AnyscaleBaseOperator):
    
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
        
        if not self.auth_token:
            self.log.info(f"Auth token is not available...")
            raise AirflowException("Auth token is not available")
        
        job_config = CreateProductionJobConfig(entrypoint = self.entrypoint,
                                               runtime_env = self.runtime_env,
                                               build_id = self.build_id,
                                               compute_config_id = self.compute_config_id,
                                               compute_config = self.compute_config,
                                               max_retries = self.max_retries)

        # Submit the job to Anyscale
        prod_job : ProductionjobResponse = self.sdk.create_job(CreateProductionJob(
                                    name=self.job_name,
                                    config=job_config))
        self.log.info(f"Submitted Anyscale job with ID: {prod_job.result.id}")

        current_status = self.get_current_status()
        self.log.info(f"Current status for {prod_job.result.id} is: {current_status.current_state}")

        if current_status in ("RUNNING","AWAITING_CLUSTER_START","PENDING","RESTARTING","UPDATING"):
            
            self.log.info(f"Deferring the polling to AnyscaleJobTrigger...")
            self.defer(trigger=AnyscaleJobTrigger(
                auth_token = self.auth_token,
                job_id = prod_job.result.id,
                job_start_time = prod_job.result.created_at,
                poll_interval = 60), 
                    method_name="execute_complete")
        elif current_status == "SUCCESS":
            self.log.info(f"Job {prod_job.result.id} completed successfully")
            return
        elif current_status in ("ERRORED","BROKEN","OUT_OF_RETRIES"):
            raise AirflowException(f"Job {prod_job.result.id} failed")
        elif current_status == "TERMINATED":
            raise AirflowException(f"Job {prod_job.result.id} was cancelled")
        else:
            raise Exception(f"Encountered unexpected state `{current_status}` for job_id `{prod_job.result.id}")
        
        return prod_job.result.id
    
    def get_current_status(self,job_id: str) -> str:
        return self.sdk.get_production_job(
                production_job_id=self.production_job_id).result.state.current_state

    def execute_complete(self, context: Context, event: TriggerEvent) -> None:

        self.production_job_id = event["production_job_id"]
        # This method gets called when the trigger fires that the job is complete
        self.log.info(f"Anyscale job {self.production_job_id} completed with status: {event['status']}")

        if event["status"] in ("OUT_OF_RETRIES", "TERMINATED", "ERRORED"):
            self.log.info(f"Anyscale job {self.production_job_id} ended with status : {event["status"]}")

        return None

