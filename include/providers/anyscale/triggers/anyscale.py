from airflow.triggers.base import BaseTrigger, TriggerEvent
import asyncio

class AnyscaleJobTrigger(BaseTrigger):
    def __init__(self, conn_id, job_id):
        super().__init__()
        self.conn_id = conn_id
        self.job_id = job_id

    def serialize(self):
        return ("custom_plugins.anyscale_triggers.AnyscaleJobTrigger", {"conn_id": self.conn_id, "job_id": self.job_id})

    async def run(self):
        # Assuming `get_job_status` is an async method in AnyscaleHook that returns the job's status
        from custom_plugins.anyscale_hooks import AnyscaleHook

        anyscale_hook = AnyscaleHook(conn_id=self.conn_id)
        while True:
            status = await anyscale_hook.get_job_status(self.job_id)
            if status in ["success", "failed"]:
                # Job finished, return control with the job's final status
                return TriggerEvent(status)
            else:
                # If the job is still running, wait for a bit before checking again
                await asyncio.sleep(30)  # Adjust the sleep time as needed
