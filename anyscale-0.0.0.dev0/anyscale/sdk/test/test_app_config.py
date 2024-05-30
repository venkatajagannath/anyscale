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
from anyscale_client.models.app_config import AppConfig  # noqa: E501
from anyscale_client.rest import ApiException

class TestAppConfig(unittest.TestCase):
    """AppConfig unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test AppConfig
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = anyscale_client.models.app_config.AppConfig()  # noqa: E501
        if include_optional :
            return AppConfig(
                id = '0', 
                name = '0', 
                project_id = '0', 
                organization_id = '0', 
                creator_id = '0', 
                created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                last_modified_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                deleted_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                is_default = True
            )
        else :
            return AppConfig(
                id = '0',
                name = '0',
                organization_id = '0',
                creator_id = '0',
                created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                last_modified_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
        )

    def testAppConfig(self):
        """Test AppConfig"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
