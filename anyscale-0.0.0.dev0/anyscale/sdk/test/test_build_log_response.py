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
from anyscale_client.models.build_log_response import BuildLogResponse  # noqa: E501
from anyscale_client.rest import ApiException

class TestBuildLogResponse(unittest.TestCase):
    """BuildLogResponse unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test BuildLogResponse
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = anyscale_client.models.build_log_response.BuildLogResponse()  # noqa: E501
        if include_optional :
            return BuildLogResponse(
                logs = '0'
            )
        else :
            return BuildLogResponse(
                logs = '0',
        )

    def testBuildLogResponse(self):
        """Test BuildLogResponse"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
