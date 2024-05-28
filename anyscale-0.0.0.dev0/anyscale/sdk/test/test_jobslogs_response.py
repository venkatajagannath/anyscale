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
from anyscale_client.models.jobslogs_response import JobslogsResponse  # noqa: E501
from anyscale_client.rest import ApiException

class TestJobslogsResponse(unittest.TestCase):
    """JobslogsResponse unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test JobslogsResponse
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = anyscale_client.models.jobslogs_response.JobslogsResponse()  # noqa: E501
        if include_optional :
            return JobslogsResponse(
                result = anyscale_client.models.jobs_logs.JobsLogs(
                    logs = '0', 
                    ready = True, )
            )
        else :
            return JobslogsResponse(
                result = anyscale_client.models.jobs_logs.JobsLogs(
                    logs = '0', 
                    ready = True, ),
        )

    def testJobslogsResponse(self):
        """Test JobslogsResponse"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
