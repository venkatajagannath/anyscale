
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
        self.job_config_kwargs = kwargs
        self.job_id = None

        if not self.entrypoint:
            raise AirflowException("Entrypoint is required.")
        if not self.job_name:
            raise AirflowException("Job name is required.")
    
    def on_kill(self):
        if self.job_id is not None:
            self.sdk.terminate_job(self.job_id)
            self.log.info("Termination request received. Submitted request to terminate the anyscale job.")
    
    @cached_property
    def hook(self) -> AnyscaleHook:
        """Return an instance of the AnyscaleHook."""
        return AnyscaleHook(conn_id=self.conn_id)

    def execute(self, context: Context):
        
        if not self.hook:
            self.log.info("SDK is not available.")
            raise AirflowException("SDK is not available.")
        
        job_config = CreateProductionJobConfig(entrypoint=self.entrypoint,
                                               runtime_env=self.runtime_env,
                                               build_id=self.build_id,
                                               compute_config_id=self.compute_config_id,
                                               compute_config=self.compute_config,
                                               max_retries=self.max_retries)

        # Submit the job to Anyscale
        prod_job = self.hook.create_job(CreateProductionJob(name=self.job_name, config=job_config))
        self.log.info(f"Submitted Anyscale job with ID: {prod_job.result.id}")

        self.job_id = prod_job.result.id
        current_status = self.get_current_status(self.job_id)
        self.log.info(f"Current status for {self.job_id} is: {current_status}")

        self.process_job_status(prod_job, current_status)
        
        return self.job_id
    
    def process_job_status(self, prod_job, current_status):
        if current_status in ("RUNNING", "AWAITING_CLUSTER_START", "PENDING", "RESTARTING", "UPDATING"):
            self.defer_job_polling(prod_job)
        elif current_status == "SUCCESS":
            self.log.info(f"Job {self.job_id} completed successfully.")
        elif current_status in ("ERRORED", "BROKEN", "OUT_OF_RETRIES"):
            raise AirflowException(f"Job {self.job_id} failed.")
        elif current_status == "TERMINATED":
            raise AirflowException(f"Job {self.job_id} was cancelled.")
        else:
            raise Exception(f"Unexpected state `{current_status}` for job_id `{self.job_id}`.")
    
    def defer_job_polling(self, prod_job):
        self.log.info("Deferring the polling to AnyscaleJobTrigger...")
        self.defer(trigger=AnyscaleJobTrigger(conn_id=self.conn_id,
                                              job_id=prod_job.result.id,
                                              job_start_time=prod_job.result.created_at,
                                              poll_interval=60),
                   method_name="execute_complete")

    def get_current_status(self, job_id):
        return self.hook.get_production_job_status(production_job_id=job_id)

    def execute_complete(self, context: Context, event: TriggerEvent) -> None:

        self.production_job_id = event["job_id"]
        
        if event["status"] in ("OUT_OF_RETRIES", "TERMINATED", "ERRORED"):
            self.log.info(f"Anyscale job {self.production_job_id} ended with status: {event['status']}")
            raise AirflowException(f"Job {self.production_job_id} failed with error {event['message']}")
        else:
            self.log.info(f"Anyscale job {self.production_job_id} completed with status: {event['status']}")
        return None

class RolloutAnyscaleService(BaseOperator):

    def __init__(self,
                conn_id: str,
                name: str,
                ray_serve_config: object,
                build_id: str,
                compute_config_id: str,
                 **kwargs):
        super(RolloutAnyscaleService, self).__init__(**kwargs)
        self.conn_id = conn_id

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
    def hook(self) -> AnyscaleHook:
        """Return an instance of the AnyscaleHook."""
        return AnyscaleHook(conn_id=self.conn_id).conn
    
    def execute(self, context):
        if not self.hook:
            self.log.info(f"SDK is not available...")
            raise AirflowException("SDK is not available")

        # Dynamically create ApplyServiceModel instance from provided parameters
        service_model = ApplyServiceModel(**self.service_params)
        
        # Call the SDK method with the dynamically created service model
        service_response = self.hook.rollout_service(apply_service_model=service_model)

        self.defer(trigger=AnyscaleServiceTrigger(conn_id = self.conn_id,
                                        service_id = service_response.result.id,
                                        expected_state = 'RUNNING',
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
            raise AirflowException(f"Job {self.service_id} failed with error {event['message']}")
        else:
            # This method gets called when the trigger fires that the job is complete
            self.log.info(f"Anyscale service deployment {self.service_id} completed with status: {event['status']}")

        return None
    

