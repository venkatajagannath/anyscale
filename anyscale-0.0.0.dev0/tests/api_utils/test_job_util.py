from typing import Tuple
from unittest.mock import Mock

import pytest

from anyscale.api_utils.exceptions.job_errors import NoJobRunError
from anyscale.api_utils.job_util import _get_job_run_id
from anyscale.sdk.anyscale_client.api.default_api import DefaultApi as BaseApi
from tests.api_utils.conftest import get_mock_base_api


def test_get_job_run_id():
    job_id = "prodjob_123"
    job_run_id = "job_123"
    # Returns from job_run_id
    assert _get_job_run_id(Mock(), job_run_id=job_run_id) == job_run_id

    # Returns from ProductionJob.last_job_run_id of job_id
    mock_prod_job = Mock(last_job_run_id=job_run_id)
    mock_base_api = get_mock_base_api(
        {BaseApi.get_production_job.__name__: Mock(result=mock_prod_job)}
    )
    assert _get_job_run_id(mock_base_api, job_id=job_id) == job_run_id

    # Raises NoJobRunError if ProductionJob.last_job_run_id is None
    mock_base_api.get_production_job.return_value.result.last_job_run_id = None
    with pytest.raises(
        NoJobRunError, match="Production job prodjob_123 has no job runs."
    ):
        _get_job_run_id(mock_base_api, job_id="prodjob_123")


@pytest.mark.parametrize("id_args", [(None, None), ("prodjob_123", "job_123")])
def test_get_job_run_id_errors_if_not_only_one_id_arg_provided(
    id_args: Tuple[str, str]
):
    job_id, job_run_id = id_args
    with pytest.raises(
        AssertionError,
        match="Exactly one of `job_id` or `job_run_id` must be provided.",
    ):
        _get_job_run_id(Mock(), job_id=job_id, job_run_id=job_run_id)
