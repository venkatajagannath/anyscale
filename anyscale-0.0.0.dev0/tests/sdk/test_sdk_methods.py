from unittest.mock import patch

from anyscale.sdk.anyscale_client.sdk import AnyscaleSDK


@patch(
    "anyscale.controllers.job_controller.JobController.__init__", return_value=None,
)
@patch(
    "anyscale.controllers.job_controller.JobController.logs", return_value=None,
)  # Patching JobController class
def test_fetch_production_job_logs(get_logs, MockedJobController):

    auth_token = "mock_auth_token"
    sdk = AnyscaleSDK(auth_token=auth_token)

    sdk.fetch_production_job_logs(job_id="mock_job_id")

    MockedJobController.assert_called_once()

    get_logs.assert_called_once()

    # Asserting auth_token parameter passed to JobController __init__ method
    _, kwargs = MockedJobController.call_args

    assert kwargs["auth_token"] == auth_token
