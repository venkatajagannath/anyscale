import os
from typing import Optional

import click
import requests

from anyscale.cli_logger import LogsLogger
from anyscale.client.openapi_client.models.create_fine_tuning_job_product_request import (
    CreateFineTuningJobProductRequest,
)
from anyscale.client.openapi_client.models.presigned_upload_file import (
    PresignedUploadFile,
)
from anyscale.client.openapi_client.models.presigned_upload_file_request import (
    PresignedUploadFileRequest,
)
from anyscale.controllers.base_controller import BaseController
from anyscale.models.fine_tune_model import FineTuneConfig
from anyscale.util import get_endpoint


class FineTuneController(BaseController):
    def __init__(
        self,
        log: Optional[LogsLogger] = None,
        initialize_auth_api_client: bool = True,
        raise_structured_exception: bool = False,
    ):
        if log is None:
            log = LogsLogger()

        super().__init__(initialize_auth_api_client, raise_structured_exception)
        self.log = log
        self.log.open_block("Output")
        self._cluster_journal_events_start_line = 0

    def _get_presigned_upload_file(
        self, file_path: str, cloud_id: str
    ) -> PresignedUploadFile:
        """
        This method gets the presigned urls from the backend and uploads the file to the cloud storage.
        """
        train_filename = os.path.basename(file_path)
        presigned_upload_file_request = PresignedUploadFileRequest(
            filename=train_filename, cloud_id=cloud_id
        )

        presigned_upload_file = self.api_client.get_file_upload_url_api_v2_files_upload_url_post(
            presigned_upload_file_request
        )

        train_file_upload_url = presigned_upload_file.presigned_url

        resolved_file_path = os.path.expanduser(file_path)
        with open(resolved_file_path, "rb") as file:
            response = requests.put(train_file_upload_url, data=file)
            if response.status_code != 200:
                self.log.error(
                    f"Status: {response.status_code}. Error: {response.text}"
                )
                raise click.ClickException(f"File upload for {file_path} failed.")

        self.log.info(f"Successfully uploaded the {file_path} to the cloud storage.")

        return presigned_upload_file

    def fine_tune(
        self, config: FineTuneConfig,
    ):
        """
        This method will upload the files to the cloud storage and then trigger the fine-tuning job.
        """
        if not os.path.isfile(config.train_file):
            self.log.error(f"Please confirm that {config.train_file} is a valid path.")
            return
        if config.valid_file and not os.path.isfile(config.valid_file):
            self.log.error(f"Please confirm that {config.valid_file} is a valid path.")
            return

        presigned_upload_train_file = self._get_presigned_upload_file(
            config.train_file, cloud_id=config.cloud_id
        )
        if config.valid_file:
            presigned_upload_valid_file = self._get_presigned_upload_file(
                config.valid_file, cloud_id=config.cloud_id
            )
            validation_file = presigned_upload_valid_file.file_id
        else:
            validation_file = None

        create_fine_tuning_job_request = CreateFineTuningJobProductRequest(
            training_file=presigned_upload_train_file.file_id,
            validation_file=validation_file,
            model=config.base_model,
            suffix=config.suffix,
            cloud_id=config.cloud_id,
            version=config.version,
            instance_type=config.instance_type,
        )
        ft_job = self.api_client.create_fine_tuning_job_api_v2_fine_tuning_jobs_create_post(
            create_fine_tuning_job_request
        ).result
        self.log.info(
            f'View the job in the UI at {get_endpoint(f"/fine-tuning/{ft_job.id}")}'
        )
