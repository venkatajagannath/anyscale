
# Standard library imports
import logging
import os

# Third-party imports
from anyscale import AnyscaleSDK
from anyscale.sdk.anyscale_client.models import *
from dataclasses import dataclass, field
from typing import Optional

# Airflow imports
from airflow.compat.functools import cached_property
from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.utils.context import Context
from airflow.models.baseoperator import BaseOperatorLink
from airflow.triggers.base import BaseTrigger, TriggerEvent
from airflow.utils.decorators import apply_defaults
from include.hooks.anyscale import AnyscaleHook
from include.triggers.anyscale import AnyscaleJobTrigger, AnyscaleServiceTrigger

logging.basicConfig(level=logging.DEBUG)

class SubmitAnyscaleJob(BaseOperator):
    
    def __init__(self,
                 conn_id : str,
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
        self.job_id = None

        if not self.entrypoint:
            raise AirflowException("Entrypoint is required.")
        if not self.job_name:
            raise AirflowException("Cluster env is required.")
    
    def on_kill(self):
        if self.job_id is not None:
            job_obj = self.sdk.terminate_job(self.job_id)
            self.log.info(f"Termination request received. Submitted request to terminate the anyscale job")
        return
    
    @cached_property
    def hook(self) -> AnyscaleHook:
        """Return an instance of the AnyscaleHook."""
        return AnyscaleHook(conn_id=self.conn_id).conn

    def execute(self, context: Context):
        
        if not self.hook:
            self.log.info(f"SDK is not available...")
            raise AirflowException("SDK is not available")
        
        job_config = CreateProductionJobConfig(entrypoint = self.entrypoint,
                                               runtime_env = self.runtime_env,
                                               build_id = self.build_id,
                                               compute_config_id = self.compute_config_id,
                                               compute_config = self.compute_config,
                                               max_retries = self.max_retries)

        # Submit the job to Anyscale
        prod_job : ProductionjobResponse = self.hook.create_job(CreateProductionJob(
                                    name=self.job_name,
                                    config=job_config))
        self.log.info(f"Submitted Anyscale job with ID: {prod_job.result.id}")

        current_status = self.get_current_status(prod_job.result.id)
        self.job_id = prod_job.result.id
        self.log.info(f"Current status for {prod_job.result.id} is: {current_status}")

        if current_status in ("RUNNING","AWAITING_CLUSTER_START","PENDING","RESTARTING","UPDATING"):
            
            self.log.info(f"Deferring the polling to AnyscaleJobTrigger...")
            self.defer(trigger=AnyscaleJobTrigger(conn_id = self.conn_id,
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
        return self.hook.get_production_job(
                production_job_id=job_id).result.state.current_state

    def execute_complete(self, context: Context, event: TriggerEvent) -> None:

        self.production_job_id = event["job_id"]
        
        if event["status"] in ("OUT_OF_RETRIES", "TERMINATED", "ERRORED"):
            self.log.info(f"Anyscale job {self.production_job_id} ended with status : {event['status']}")
        else:
            # This method gets called when the trigger fires that the job is complete
            self.log.info(f"Anyscale job {self.production_job_id} completed with status: {event['status']}")

        return None

class RolloutAnyscaleService(BaseOperator):

    def __init__(self,
                auth_token: str,
                name: str,
                ray_serve_config: object,
                build_id: str,
                compute_config_id: str,
                 **kwargs):
        super(RolloutAnyscaleService, self).__init__(**kwargs)
        self.auth_token = auth_token

        # Set up explicit parameters
        self.service_params = {
            'name': name,
            'ray_serve_config': ray_serve_config,
            'build_id': build_id,
            'compute_config_id': compute_config_id
        }

        # Remove specific keys from kwargs which are related to Airflow infrastructure
        for key in ['task_id', 'dag', 'default_args', 'owner', 'email', 'start_date','depends_on_past','email_on_failure','email_on_retry','retries','retry_delay']:
            kwargs.pop(key, None)  # Use pop with default to avoid KeyError

        self.service_params.update(kwargs)

    @cached_property
    def sdk(self) -> 'AnyscaleSDK':  # Assuming AnyscaleSDK is defined somewhere
        return AnyscaleSDK(auth_token=self.auth_token)
    
    def execute(self, context):
        if not self.auth_token:
            self.log.info("Auth token is not available...")
            raise AirflowException("Auth token is not available")

        # Dynamically create ApplyServiceModel instance from provided parameters
        service_model = ApplyServiceModel(**self.service_params)
        
        # Call the SDK method with the dynamically created service model
        service_response = self.sdk.rollout_service(apply_service_model=service_model)

        self.defer(trigger=AnyscaleServiceTrigger(auth_token = self.auth_token,
                                        service_id = service_response.result.id,
                                        expected_state = service_response.result.goal_state,
                                        poll_interval= 60,
                                        timeout= 600),
            method_name="execute_complete")

        self.log.info(f"Service rollout response: {service_response}")
        
        return service_response
    
    def execute_complete(self, context: Context, event: TriggerEvent) -> None:
        self.log.info(f"Execution completed...")

        self.service_id = event["service_id"]
        
        if event["status"] == 'failed':
            self.log.info(f"Anyscale service deployment {self.service_id} ended with status : {event['status']}")
        else:
            # This method gets called when the trigger fires that the job is complete
            self.log.info(f"Anyscale service deployment {self.service_id} completed with status: {event['status']}")

        return None
    

