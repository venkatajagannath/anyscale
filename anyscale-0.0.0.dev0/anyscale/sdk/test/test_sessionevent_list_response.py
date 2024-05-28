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
from anyscale_client.models.sessionevent_list_response import SessioneventListResponse  # noqa: E501
from anyscale_client.rest import ApiException

class TestSessioneventListResponse(unittest.TestCase):
    """SessioneventListResponse unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test SessioneventListResponse
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = anyscale_client.models.sessionevent_list_response.SessioneventListResponse()  # noqa: E501
        if include_optional :
            return SessioneventListResponse(
                results = [
                    anyscale_client.models.session_event.SessionEvent(
                        event_type = '0', 
                        log_level = null, 
                        timestamp = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        description = '0', 
                        cause = null, 
                        id = '0', )
                    ], 
                metadata = null
            )
        else :
            return SessioneventListResponse(
                results = [
                    anyscale_client.models.session_event.SessionEvent(
                        event_type = '0', 
                        log_level = null, 
                        timestamp = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        description = '0', 
                        cause = null, 
                        id = '0', )
                    ],
        )

    def testSessioneventListResponse(self):
        """Test SessioneventListResponse"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
