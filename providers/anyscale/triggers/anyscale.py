from airflow.triggers.base import BaseTrigger, TriggerEvent
import asyncio
from typing import Any
import time
from datetime import datetime

from airflow.compat.functools import cached_property
from anyscale import AnyscaleSDK

class AnyscaleJobTrigger(BaseTrigger):
    def __init__(self,
                auth_token: str,
                job_id: str,
                job_start_time: datetime,
                poll_interval: int = 60):
        super().__init__()
        self.auth_token = auth_token
        self.job_id = job_id
        self.job_start_time = job_start_time
        self.poll_interval = poll_interval

    @cached_property
    def sdk(self) -> AnyscaleSDK:
        return AnyscaleSDK(auth_token=self.auth_token)

    def serialize(self):
        return ("providers.anyscale.triggers.anyscale.AnyscaleJobTrigger", 
                {"job_id": self.job_id})

    async def run(self):

        if not self.job_id:
            yield TriggerEvent({"status": "error", "message": "No job_id provided to async trigger", "job_id": self.job_id})
        
        try:
            self.log.info(f"Polling for job {self.job_id} every {self.poll_interval} seconds...")
            
            while self.check_current_status():
                if self.end_time < time.time():
                    yield TriggerEvent(
                        {
                            "status": "error",
                            "message": f"Job run {self.job_id} has not reached a terminal status after "
                            f"{self.end_time} seconds.",
                            "job_id": self.job_id,
                        }
                    )
                    return
                await asyncio.sleep(self.poll_interval)
            self.log.info(f"Job {self.job_id}completed execution before the timeout period...")
            
            completed_status = self.get_current_status(self.job_id)
            self.log.info(f"Status of completed job {self.job_id} is: {completed_status.current_state}")
            if completed_status.current_state == 'SUCCESS':
                yield TriggerEvent(
                    {
                        "status": completed_status.current_state,
                        "message": f"Job run {self.job_id} has completed successfully.",
                        "job_id": self.job_id,
                        "elapsed_time": completed_status.state_transitioned_at - self.job_start_time
                    }
                )
            elif completed_status.current_state in ("OUT_OF_RETRIES", "TERMINATED", "ERRORED"):
                yield TriggerEvent(
                    {
                        "status": completed_status.current_state,
                        "message": f"Job run {self.job_id} has been stopped.",
                        "job_id": self.job_id,
                        "elapsed_time": completed_status.state_transitioned_at - self.job_start_time
                    }
                )
            else:
                yield TriggerEvent(
                    {
                        "status": completed_status.current_state,
                        "message": f"Job run {self.job_id} has failed.",
                        "job_id": self.job_id,
                        "elapsed_time": completed_status.state_transitioned_at - self.job_start_time
                    }
                )
        except Exception as e:
            yield TriggerEvent({"status": "error", "message": str(e), "job_id": self.job_id})

    def get_current_status(self,job_id: str):
        return self.sdk.get_production_job(
                production_job_id=self.production_job_id).result.state
        
    def check_current_status(self,job_id: str) -> str:
        job_status = self.sdk.get_production_job(
                production_job_id=self.production_job_id).result.state.current_state
        self.log.info(f"Current job status for {self.job_id} is: {job_status}")
        if job_status in ('RUNNING','PENDING','AWAITING_CLUSTER_START','RESTARTING'):
            return True
        else:
            return False
