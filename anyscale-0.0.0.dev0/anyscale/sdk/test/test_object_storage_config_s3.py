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
from anyscale_client.models.object_storage_config_s3 import ObjectStorageConfigS3  # noqa: E501
from anyscale_client.rest import ApiException

class TestObjectStorageConfigS3(unittest.TestCase):
    """ObjectStorageConfigS3 unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test ObjectStorageConfigS3
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = anyscale_client.models.object_storage_config_s3.ObjectStorageConfigS3()  # noqa: E501
        if include_optional :
            return ObjectStorageConfigS3(
                region = '0', 
                bucket = '0', 
                path = '0', 
                aws_access_key_id = '0', 
                aws_secret_access_key = '0', 
                aws_session_token = '0'
            )
        else :
            return ObjectStorageConfigS3(
                region = '0',
                bucket = '0',
                path = '0',
                aws_access_key_id = '0',
                aws_secret_access_key = '0',
                aws_session_token = '0',
        )

    def testObjectStorageConfigS3(self):
        """Test ObjectStorageConfigS3"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
