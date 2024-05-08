import unittest
from unittest.mock import patch, MagicMock
from airflow.exceptions import AirflowException
from anyscale_provider.hooks.anyscale import AnyscaleHook
from anyscale import AnyscaleSDK

class TestAnyscaleHook(unittest.TestCase):

    def setUp(self):
        self.hook = AnyscaleHook(conn_id='test_conn')

    @patch('include.hooks.anyscale.AnyscaleHook.get_connection')
    def test_connection_initialization(self, mock_get_connection):
        mock_get_connection.return_value.password = 'fake_api_key'
        sdk = self.hook.conn
        self.assertIsInstance(sdk, AnyscaleSDK)

    @patch.object(AnyscaleHook, 'get_sdk')
    def test_create_job(self, mock_get_sdk):
        config = {'job_type': 'Production'}
        mock_get_sdk.return_value.create_job.return_value = 'job1234'
        job_id = self.hook.create_job(config)
        self.assertEqual(job_id, 'job1234')

    @patch.object(AnyscaleHook, 'get_sdk')
    def test_fetch_production_job_logs(self, mock_get_sdk):
        logs_output = "Log line 1\nLog line 2"
        mock_get_sdk.return_value.fetch_production_job_logs.return_value = logs_output
        logs = self.hook.fetch_production_job_logs('job1234')
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs, ["Log line 1", "Log line 2"])

    @patch.object(AnyscaleHook, 'get_sdk')
    def test_terminate_job_success(self, mock_get_sdk):
        mock_get_sdk.return_value.terminate_job.return_value = MagicMock(result=MagicMock(state=MagicMock(goal_state='TERMINATED')))
        result = self.hook.terminate_job('job1234')
        self.assertTrue(result)

    @patch('include.hooks.anyscale.AnyscaleHook.get_connection')
    def test_conn_failure_raises_exception(self, mock_get_connection):
        mock_get_connection.return_value.password = None  # No API token provided
        with self.assertRaises(AirflowException) as context:
            _ = self.hook.conn  # Access to trigger the connection
        self.assertIn("Missing API token", str(context.exception))
