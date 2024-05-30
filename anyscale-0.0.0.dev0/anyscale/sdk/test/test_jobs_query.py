# coding: utf-8

"""
    Anyscale API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import anyscale_client
from anyscale_client.models.jobs_query import JobsQuery  # noqa: E501
from anyscale_client.rest import ApiException

class TestJobsQuery(unittest.TestCase):
    """JobsQuery unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test JobsQuery
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = anyscale_client.models.jobs_query.JobsQuery()  # noqa: E501
        if include_optional :
            return JobsQuery(
                name = null, 
                runtime_environment_id = '0', 
                cluster_id = '0', 
                creator_id = '0', 
                ray_job_id = '0', 
                project_id = '0', 
                include_child_jobs = True, 
                ha_job_id = '0', 
                show_ray_client_runs_only = True, 
                paging = null, 
                state_filter = [
                    'RUNNING'
                    ], 
                type_filter = [
                    'INTERACTIVE_SESSION'
                    ], 
                sort_by_clauses = [
                    anyscale_client.models.sort_by_clause[jobs_sort_field].SortByClause[JobsSortField](
                        sort_field = 'STATUS', 
                        sort_order = 'ASC', )
                    ]
            )
        else :
            return JobsQuery(
        )

    def testJobsQuery(self):
        """Test JobsQuery"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
