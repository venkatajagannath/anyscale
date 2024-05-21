
# Standard library imports
import logging
import os
import time
from typing import List, Dict, Union

# Third-party imports
import anyscale
from anyscale.compute_config.models import (
    ComputeConfig, HeadNodeConfig, MarketType, WorkerNodeGroupConfig
)

# Airflow imports
from airflow.compat.functools import cached_property
from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.utils.context import Context
from airflow.triggers.base import TriggerEvent
from airflow.utils.decorators import apply_defaults
from include.hooks.anyscale import AnyscaleHook,AnyscaleHook_
from include.triggers.anyscale import AnyscaleJobTrigger, AnyscaleServiceTrigger

logging.basicConfig(level=logging.DEBUG)

class SubmitAnyscaleJob(BaseOperator):
    
    def __init__(self,
                 conn_id: str,
                 name: str,
                 image_uri: str,
                 compute_config: Union[ComputeConfig, dict, str],
                 working_dir: str,
                 excludes: List[str],
                 requirements: Union[str, List[str]],
                 env_vars: Dict[str, str],
                 py_modules: List[str],
                 entrypoint: str,
                 max_retries: int,
                 *args, **kwargs):
        super(SubmitAnyscaleJob, self).__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.name = name
        self.image_uri = image_uri
        self.compute_config = compute_config
        self.working_dir = working_dir
        self.excludes = excludes
        self.requirements = requirements
        self.env_vars = env_vars
        self.py_modules = py_modules
        self.entrypoint = entrypoint
        self.max_retries = max_retries

        self.job_id = None
        self.created_at = None

        self.fields = {
            "name": name,
            "image_uri": image_uri,
            "compute_config": compute_config,
            "working_dir": working_dir,
            "excludes": excludes,
            "requirements": requirements,
            "env_vars": env_vars,
            "py_modules": py_modules,
            "entrypoint": entrypoint,
            "max_retries": max_retries
        }

        if not self.name:
            raise AirflowException("Job name is required.")
        
        # Ensure entrypoint is not empty
        if not self.entrypoint:
            raise AirflowException("Entrypoint must be specified.")
    
    def on_kill(self):
        if self.job_id is not None:
            self.hook.terminate_job(self.job_id)
            self.log.info("Termination request received. Submitted request to terminate the anyscale job.")
        return self.job_id
    
    @cached_property
    def hook(self) -> AnyscaleHook_:
        """Return an instance of the AnyscaleHook."""
        return AnyscaleHook_(conn_id=self.conn_id)

    def execute(self, context: Context):
        
        if not self.hook:
            self.log.info("SDK is not available.")
            raise AirflowException("SDK is not available.")
        else:
            self.log.info(f"Using Anyscale version {anyscale.__version__}")

        # Submit the job to Anyscale
        self.job_id = self.hook.submit_job(self.fields)
        self.created_at = time.time()
        self.log.info(f"Submitted Anyscale job with ID: {self.job_id}")

        current_status = self.get_current_status(self.job_id)
        self.log.info(f"Current status for {self.job_id} is: {current_status}")

        self.process_job_status(self.job_id, current_status)
        
        return self.job_id
    
    def process_job_status(self, job_id, current_status):
        if current_status in ("RUNNING", "AWAITING_CLUSTER_START", "PENDING", "RESTARTING", "UPDATING"):
            self.defer_job_polling(job_id)
        elif current_status == "SUCCESS":
            self.log.info(f"Job {job_id} completed successfully.")
        elif current_status in ("ERRORED", "BROKEN", "OUT_OF_RETRIES"):
            raise AirflowException(f"Job {job_id} failed.")
        elif current_status == "TERMINATED":
            raise AirflowException(f"Job {job_id} was cancelled.")
        else:
            raise Exception(f"Unexpected state `{current_status}` for job_id `{job_id}`.")
    
    def defer_job_polling(self, job_id):
        self.log.info("Deferring the polling to AnyscaleJobTrigger...")
        self.defer(trigger=AnyscaleJobTrigger(conn_id=self.conn_id,
                                              job_id = job_id,
                                              job_start_time=self.created_at,
                                              poll_interval=60),
                   method_name="execute_complete")

    def get_current_status(self, job_id):
        return self.hook.get_job_status(job_id=job_id)

    def execute_complete(self, context: Context, event: TriggerEvent) -> None:

        current_job_id = event["job_id"]
        
        if event["status"] in ("OUT_OF_RETRIES", "TERMINATED", "ERRORED"):
            self.log.info(f"Anyscale job {current_job_id} ended with status: {event['status']}")
            raise AirflowException(f"Job {current_job_id} failed with error {event['message']}")
        else:
            self.log.info(f"Anyscale job {current_job_id} completed with status: {event['status']}")
        return None

class RolloutAnyscaleService(BaseOperator):

    def __init__(self,
                conn_id: str,
                name: str,
                ray_serve_config: object,
                build_id: str,
                compute_config_id: str,
                description: str = None,
                project_id: str = None,
                version: str = None,
                canary_percent: int = None,
                config: dict = None,
                rollout_strategy: str = None,
                ray_gcs_external_storage_config: dict = None,
                auto_complete_rollout: bool = None,
                max_surge_percent: int = None,
                **kwargs):
        super(RolloutAnyscaleService, self).__init__(**kwargs)
        self.conn_id = conn_id

        # Set up explicit parameters
        self.service_params = {
            'name': name,
            'ray_serve_config': ray_serve_config,
            'build_id': build_id,
            'compute_config_id': compute_config_id,
            'description': description,
            'project_id': project_id,
            'version': version,
            'canary_percent': canary_percent,
            'config': config,
            'rollout_strategy': rollout_strategy,
            'ray_gcs_external_storage_config': ray_gcs_external_storage_config,
            'auto_complete_rollout': auto_complete_rollout,
            'max_surge_percent': max_surge_percent
        }

    @cached_property
    def hook(self) -> AnyscaleHook:
        """Return an instance of the AnyscaleHook."""
        return AnyscaleHook(conn_id=self.conn_id)
    
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
    

