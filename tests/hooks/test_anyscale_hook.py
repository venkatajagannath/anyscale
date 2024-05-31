import unittest
from unittest import mock
from unittest.mock import patch, MagicMock, Mock
from airflow.exceptions import AirflowException
from airflow.models import Connection
from airflow.utils import db
from anyscale_provider.hooks.anyscale import AnyscaleHook
from anyscale.job.models import JobConfig
from anyscale.service.models import ServiceConfig


anyscale_client_mock = Mock(name="anyscale_client_for_test")

class TestAnyscaleHook:

    def setup_method(self):

        db.merge_conn(
            Connection(
                conn_id="anyscale_default",
                conn_type="anyscale",
                password="password"
            )
        )

    @patch.object(AnyscaleHook, 'submit_job')
    def test_submit_job(self,mock_submit_job):
        config = JobConfig(name='Production',entrypoint="python script.py")
        mock_submit_job.return_value.job.submit.return_value = 'job1234'
        job_id = self.hook.submit_job(config)
        self.assertEqual(job_id, 'job1234')

    @patch.object(AnyscaleHook, 'get_connection')
    @patch.object(AnyscaleHook, 'get_sdk')
    def test_deploy_service(self, mock_get_sdk, mock_get_connection):
        config = ServiceConfig(service_type='Production')
        mock_conn = MagicMock()
        mock_conn.password = 'test_token'
        mock_get_connection.return_value = mock_conn
        mock_get_sdk.return_value.service.deploy.return_value = 'service1234'
        service_id = self.hook.deploy_service(config)
        self.assertEqual(service_id, 'service1234')

    @patch.object(AnyscaleHook, 'get_connection')
    @patch.object(AnyscaleHook, 'get_sdk')
    def test_get_job_status(self, mock_get_sdk, mock_get_connection):
        mock_conn = MagicMock()
        mock_conn.password = 'test_token'
        mock_get_connection.return_value = mock_conn
        mock_get_sdk.return_value.job.status.return_value = 'Running'
        status = self.hook.get_job_status('job1234')
        self.assertEqual(status, 'Running')

    @patch.object(AnyscaleHook, 'get_connection')
    @patch.object(AnyscaleHook, 'get_sdk')
    def test_get_service_status(self, mock_get_sdk, mock_get_connection):
        mock_conn = MagicMock()
        mock_conn.password = 'test_token'
        mock_get_connection.return_value = mock_conn
        mock_get_sdk.return_value.service.status.return_value = 'Running'
        status = self.hook.get_service_status('service_name')
        self.assertEqual(status, 'Running')

    @patch.object(AnyscaleHook, 'get_connection')
    @patch.object(AnyscaleHook, 'get_sdk')
    def test_terminate_job_success(self, mock_get_sdk, mock_get_connection):
        mock_conn = MagicMock()
        mock_conn.password = 'test_token'
        mock_get_connection.return_value = mock_conn
        mock_get_sdk.return_value.job.terminate.return_value = 'job1234'
        result = self.hook.terminate_job('job1234', time_delay=1)
        self.assertTrue(result)

    @patch.object(AnyscaleHook, 'get_connection')
    @patch.object(AnyscaleHook, 'get_sdk')
    def test_terminate_service_success(self, mock_get_sdk, mock_get_connection):
        mock_conn = MagicMock()
        mock_conn.password = 'test_token'
        mock_get_connection.return_value = mock_conn
        mock_get_sdk.return_value.service.terminate.return_value = 'service1234'
        result = self.hook.terminate_service('service1234', time_delay=1)
        self.assertTrue(result)

    @patch.object(AnyscaleHook, 'get_connection')
    @patch.object(AnyscaleHook, 'get_sdk')
    def test_fetch_logs(self, mock_get_sdk, mock_get_connection):
        logs_output = "Log line 1\nLog line 2"
        mock_conn = MagicMock()
        mock_conn.password = 'test_token'
        mock_get_connection.return_value = mock_conn
        mock_get_sdk.return_value.job.logs.return_value = logs_output
        logs = self.hook.fetch_logs('job1234')
        self.assertEqual(len(logs.split('\n')), 2)
        self.assertEqual(logs, "Log line 1\nLog line 2")

if __name__ == '__main__':
    unittest.main()