# coding: utf-8

"""
    Managed Ray API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from openapi_client.configuration import Configuration


class AicaendpointeventListResponse(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'results': 'list[AicaEndpointEvent]',
        'metadata': 'ListResponseMetadata'
    }

    attribute_map = {
        'results': 'results',
        'metadata': 'metadata'
    }

    def __init__(self, results=None, metadata=None, local_vars_configuration=None):  # noqa: E501
        """AicaendpointeventListResponse - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._results = None
        self._metadata = None
        self.discriminator = None

        self.results = results
        if metadata is not None:
            self.metadata = metadata

    @property
    def results(self):
        """Gets the results of this AicaendpointeventListResponse.  # noqa: E501


        :return: The results of this AicaendpointeventListResponse.  # noqa: E501
        :rtype: list[AicaEndpointEvent]
        """
        return self._results

    @results.setter
    def results(self, results):
        """Sets the results of this AicaendpointeventListResponse.


        :param results: The results of this AicaendpointeventListResponse.  # noqa: E501
        :type: list[AicaEndpointEvent]
        """
        if self.local_vars_configuration.client_side_validation and results is None:  # noqa: E501
            raise ValueError("Invalid value for `results`, must not be `None`")  # noqa: E501

        self._results = results

    @property
    def metadata(self):
        """Gets the metadata of this AicaendpointeventListResponse.  # noqa: E501


        :return: The metadata of this AicaendpointeventListResponse.  # noqa: E501
        :rtype: ListResponseMetadata
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Sets the metadata of this AicaendpointeventListResponse.


        :param metadata: The metadata of this AicaendpointeventListResponse.  # noqa: E501
        :type: ListResponseMetadata
        """

        self._metadata = metadata

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, AicaendpointeventListResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AicaendpointeventListResponse):
            return True

        return self.to_dict() != other.to_dict()
