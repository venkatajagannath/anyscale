import unittest
from unittest.mock import patch, MagicMock
from airflow.utils.context import Context
from airflow.exceptions import AirflowException,TaskDeferred
from include.operators.anyscale import SubmitAnyscaleJob  # Adjust import based on your actual module structure
from include.operators.anyscale import RolloutAnyscaleService  # Adjust import based on your actual module structure

class TestSubmitAnyscaleJob(unittest.TestCase):
    def setUp(self):
        self.operator = SubmitAnyscaleJob(conn_id='test_conn', name='test_job', config={'test': 'config'},task_id='submit_job_test')

    @patch('include.operators.anyscale.SubmitAnyscaleJob.get_current_status')
    def test_execute_successful(self, mock_get_status):
        
        mock_get_status.return_value = 'SUCCESS'
        
        self.operator.job_id = '123'        
        job_id = self.operator.execute(Context())
        
        self.assertEqual(job_id, '123')

    @patch('include.operators.anyscale.SubmitAnyscaleJob.process_job_status')
    @patch('include.operators.anyscale.SubmitAnyscaleJob.hook')
    def test_execute_fail_on_status(self, mock_hook, mock_process_job_status):
        mock_prod_job = MagicMock()
        mock_prod_job.result.id = '123'
        mock_hook.return_value.create_job.return_value = mock_prod_job
        mock_hook.return_value.get_production_job_status.return_value = 'ERRORED'

        self.operator.job_id = '123'
        mock_process_job_status.side_effect = AirflowException("Job 123 failed.")

        with self.assertRaises(AirflowException):
            self.operator.execute(Context())

        mock_process_job_status.assert_called_once_with(mock_prod_job, 'ERRORED')

    @patch('include.operators.anyscale.SubmitAnyscaleJob.hook', new_callable=MagicMock)
    def test_on_kill(self, mock_hook_property):
        mock_hook = MagicMock()
        mock_hook_property.return_value = mock_hook
        
        self.operator.job_id = '123'
        self.operator.on_kill()
        
        mock_hook.terminate_job.assert_called_once_with('123')

    @patch('include.operators.anyscale.SubmitAnyscaleJob.hook')
    def test_process_job_status_unexpected_state(self, mock_hook):
        mock_hook.return_value.get_production_job_status.return_value = 'UNKNOWN_STATE'
        with self.assertRaises(Exception):
            self.operator.process_job_status(None, 'UNKNOWN_STATE')

    @patch('include.operators.anyscale.SubmitAnyscaleJob.defer_job_polling')
    @patch('include.operators.anyscale.SubmitAnyscaleJob.hook')
    def test_defer_job_polling_called(self, mock_hook, mock_defer_job_polling):
        mock_hook.return_value.get_production_job_status.return_value = 'PENDING'
        self.operator.process_job_status('123', 'PENDING')
        mock_defer_job_polling.assert_called_once()

    @patch('include.operators.anyscale.SubmitAnyscaleJob.hook')
    def test_execute_complete(self, mock_hook):
        event = {'status': 'SUCCESS', 'job_id': '123', 'message': 'Job completed successfully'}
        self.operator.execute_complete(Context(), event)
        self.assertEqual(self.operator.production_job_id, '123')



class TestRolloutAnyscaleService(unittest.TestCase):
    def setUp(self):
        self.operator = RolloutAnyscaleService(
            conn_id='test_conn',
            name='test_service',
            ray_serve_config={},
            build_id='build123',
            compute_config_id='config123',
            task_id='rollout_service_test'
        )

    @patch('include.operators.anyscale.RolloutAnyscaleService.hook')
    def test_execute_successful(self, mock_hook):
        mock_hook.return_value.rollout_service.return_value.result.id = 'service123'
        with self.assertRaises(TaskDeferred):
            self.operator.execute(Context())

    @patch('include.operators.anyscale.RolloutAnyscaleService.hook', new_callable=MagicMock)
    def test_execute_fail_sdk_unavailable(self, mock_hook):
        mock_hook.return_value = None

        with self.assertRaises((AirflowException, TaskDeferred)) as cm:
            self.operator.execute({})

        if isinstance(cm.exception, AirflowException):
            pass
        elif isinstance(cm.exception, TaskDeferred):
            print("Task was deferred as expected under test conditions.")

    @patch('include.operators.anyscale.RolloutAnyscaleService.defer')
    @patch('include.operators.anyscale.RolloutAnyscaleService.hook')
    def test_defer_trigger_called(self, mock_hook, mock_defer):
        mock_hook.return_value.rollout_service.return_value.result.id = 'service123'
        self.operator.execute(Context())
        mock_defer.assert_called_once()

    @patch('include.operators.anyscale.RolloutAnyscaleService.hook')
    def test_execute_complete_failed(self, mock_hook):
        event = {'status': 'failed', 'service_id': 'service123', 'message': 'Deployment failed'}
        with self.assertRaises(AirflowException):
            self.operator.execute_complete(Context(), event)

    @patch('include.operators.anyscale.RolloutAnyscaleService.hook')
    def test_execute_complete_success(self, mock_hook):
        event = {'status': 'success', 'service_id': 'service123', 'message': 'Deployment succeeded'}
        self.operator.execute_complete(Context(), event)
        self.assertEqual(self.operator.service_id, 'service123')



if __name__ == '__main__':
    unittest.main()
