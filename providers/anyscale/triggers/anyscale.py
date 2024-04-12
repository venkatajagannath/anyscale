from airflow.triggers.base import BaseTrigger, TriggerEvent
import asyncio
import time
from datetime import datetime, timedelta
from airflow.compat.functools import cached_property
from anyscale import AnyscaleSDK
import logging

class AnyscaleJobTrigger(BaseTrigger):
    def __init__(self,
                 auth_token: str,
                 job_id: str,
                 job_start_time: datetime,
                 poll_interval: int = 60,
                 timeout: int = 600):  # Default timeout after an hour
        super().__init__()
        self.auth_token = auth_token
        self.job_id = job_id
        self.job_start_time = job_start_time
        self.poll_interval = poll_interval
        self.end_time = time.time() + timeout

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    @cached_property
    def sdk(self) -> AnyscaleSDK:
        return AnyscaleSDK(auth_token=self.auth_token)

    def serialize(self):
        return ("providers.anyscale.triggers.anyscale.AnyscaleJobTrigger", 
                {
                    "auth_token": self.auth_token,
                    "job_id": self.job_id,
                    "job_start_time": self.job_start_time.isoformat(),
                    "poll_interval": self.poll_interval
                })

    async def run(self):
        if not self.job_id:
            self.logger("No job_id provided")
            yield TriggerEvent({"status": "error", "message": "No job_id provided to async trigger", "job_id": self.job_id})
        try:
            self.logger.info(f"Polling for job {self.job_id} every {self.poll_interval} seconds...")
            while self.check_current_status(self.job_id):
                if time.time() > self.end_time:
                    yield TriggerEvent(
                        {
                            "status": "timeout",
                            "message": f"Job {self.job_id} has not reached a terminal status after timeout.",
                            "job_id": self.job_id,
                        }
                    )
                    return
                await asyncio.sleep(self.poll_interval)

            self.logger.info(f"Job {self.job_id} completed execution before the timeout period...")
            completed_status = self.get_current_status(self.job_id)
            yield TriggerEvent(
                {
                    "status": completed_status,
                    "message": f"Job run {self.job_id} has completed with status {completed_status}.",
                    "job_id": self.job_id
                }
            )
        except Exception as e:
            self.logger.error("An error occurred:", exc_info=True)
            yield TriggerEvent({"status": "error", "message": str(e), "job_id": self.job_id})

    def get_current_status(self, job_id: str):
        return self.sdk.get_production_job(production_job_id=job_id).result.state.current_state
        
    def check_current_status(self, job_id: str) -> bool:
        job_status = self.get_current_status(job_id)
        self.logger.info(f"Current job status for {job_id} is: {job_status}")
        return job_status in ('RUNNING', 'PENDING', 'AWAITING_CLUSTER_START', 'RESTARTING')
