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
            self.logger.info("No job_id provided")
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


class AnyscaleServiceTrigger(BaseTrigger):
    def __init__(self,
                 auth_token: str,
                 service_id: str,
                 expected_state: str,
                 poll_interval: int = 60,
                 timeout: int = 600):
        super().__init__()
        self.auth_token = auth_token
        self.service_id = service_id
        self.expected_state = expected_state
        self.poll_interval = poll_interval
        self.timeout = timeout

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.end_time = time.time() + timeout

    @cached_property
    def sdk(self) -> AnyscaleSDK:
        return AnyscaleSDK(auth_token=self.auth_token)

    def serialize(self):
        return ("providers.anyscale.triggers.anyscale.AnyscaleServiceTrigger", {
            "auth_token": self.auth_token,
            "service_id": self.service_id,
            "expected_state": self.expected_state,
            "poll_interval": self.poll_interval,
            "timeout": self.timeout
        })

    async def run(self):
        
        if not self.service_id:
            self.logger.info("No service_id provided")
            yield TriggerEvent({"status": "error", "message": "No service_id provided to async trigger", "service_id": self.service_id})

        try:
            self.logger.info(f"Monitoring service {self.service_id} every {self.poll_interval} seconds to reach {self.expected_state}")
            while self.check_current_status(self.service_id):
                if time.time() > self.end_time:
                    yield TriggerEvent({
                        "status": "timeout",
                        "message": f"Service {self.service_id} did not reach {self.expected_state} within the timeout period.",
                        "service_id": self.service_id
                    })
                    return

                current_state = self.get_current_status(self.service_id)
                self.logger.info(f"Current state of service {self.service_id}: {current_state}")

                if current_state == self.expected_state:
                    yield TriggerEvent({"status": "success",
                                        "message":"Service deployment succeeded",
                                        "service_id": self.service_id})
                    return
                elif current_state == 'UNHEALTHY' and self.expected_state != 'UNHEALTHY':
                    yield TriggerEvent({
                        "status": "failed",
                        "message": f"Service {self.service_id} entered an unexpected state: {current_state}",
                        "service_id": self.service_id
                    })
                    return

                await asyncio.sleep(self.poll_interval)

        except Exception as e:
            self.logger.error("An error occurred during monitoring:", exc_info=True)
            yield TriggerEvent({"status": "error", "message": str(e),"service_id": self.service_id})
    
    def get_current_status(self, service_id: str):
        return self.sdk.get_service(service_id).result.current_state
        
    def check_current_status(self, service_id: str) -> bool:
        job_status = self.get_current_status(service_id)
        self.logger.info(f"Current job status for {service_id} is: {job_status}")
        return job_status in ('STARTING','UPDATING', 'ROLLING_OUT')
