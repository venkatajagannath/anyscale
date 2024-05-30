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
from anyscale_client.models.cluster_services_urls import ClusterServicesUrls  # noqa: E501
from anyscale_client.rest import ApiException

class TestClusterServicesUrls(unittest.TestCase):
    """ClusterServicesUrls unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test ClusterServicesUrls
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = anyscale_client.models.cluster_services_urls.ClusterServicesUrls()  # noqa: E501
        if include_optional :
            return ClusterServicesUrls(
                webterminal_auth_url = '0', 
                metrics_dashboard_url = '0', 
                persistent_metrics_url = '0', 
                connect_url = '0', 
                jupyter_notebook_url = '0', 
                ray_dashboard_url = '0', 
                service_proxy_url = '0', 
                user_service_url = '0'
            )
        else :
            return ClusterServicesUrls(
        )

    def testClusterServicesUrls(self):
        """Test ClusterServicesUrls"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
