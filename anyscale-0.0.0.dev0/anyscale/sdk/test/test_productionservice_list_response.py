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
from anyscale_client.models.productionservice_list_response import ProductionserviceListResponse  # noqa: E501
from anyscale_client.rest import ApiException

class TestProductionserviceListResponse(unittest.TestCase):
    """ProductionserviceListResponse unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test ProductionserviceListResponse
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = anyscale_client.models.productionservice_list_response.ProductionserviceListResponse()  # noqa: E501
        if include_optional :
            return ProductionserviceListResponse(
                results = [
                    anyscale_client.models.production_service.ProductionService(
                        id = '0', 
                        name = '0', 
                        description = '0', 
                        created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        creator_id = '0', 
                        config = null, 
                        state = null, 
                        project_id = '0', 
                        last_job_run_id = '0', 
                        url = '0', 
                        token = '0', 
                        access = null, 
                        healthcheck_url = '0', )
                    ], 
                metadata = null
            )
        else :
            return ProductionserviceListResponse(
                results = [
                    anyscale_client.models.production_service.ProductionService(
                        id = '0', 
                        name = '0', 
                        description = '0', 
                        created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        creator_id = '0', 
                        config = null, 
                        state = null, 
                        project_id = '0', 
                        last_job_run_id = '0', 
                        url = '0', 
                        token = '0', 
                        access = null, 
                        healthcheck_url = '0', )
                    ],
        )

    def testProductionserviceListResponse(self):
        """Test ProductionserviceListResponse"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
