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


class CloudDataBucketPresignedUploadRequest(object):
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
        'file_type': 'CloudDataBucketFileType',
        'file_name': 'str'
    }

    attribute_map = {
        'file_type': 'file_type',
        'file_name': 'file_name'
    }

    def __init__(self, file_type=None, file_name=None, local_vars_configuration=None):  # noqa: E501
        """CloudDataBucketPresignedUploadRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._file_type = None
        self._file_name = None
        self.discriminator = None

        self.file_type = file_type
        self.file_name = file_name

    @property
    def file_type(self):
        """Gets the file_type of this CloudDataBucketPresignedUploadRequest.  # noqa: E501

        The type of file that will be uploaded (e.g. 'runtime_env_packages').  # noqa: E501

        :return: The file_type of this CloudDataBucketPresignedUploadRequest.  # noqa: E501
        :rtype: CloudDataBucketFileType
        """
        return self._file_type

    @file_type.setter
    def file_type(self, file_type):
        """Sets the file_type of this CloudDataBucketPresignedUploadRequest.

        The type of file that will be uploaded (e.g. 'runtime_env_packages').  # noqa: E501

        :param file_type: The file_type of this CloudDataBucketPresignedUploadRequest.  # noqa: E501
        :type: CloudDataBucketFileType
        """
        if self.local_vars_configuration.client_side_validation and file_type is None:  # noqa: E501
            raise ValueError("Invalid value for `file_type`, must not be `None`")  # noqa: E501

        self._file_type = file_type

    @property
    def file_name(self):
        """Gets the file_name of this CloudDataBucketPresignedUploadRequest.  # noqa: E501

        The name of the file that will be uploaded (e.g. 'runtime_env_1234.zip').  # noqa: E501

        :return: The file_name of this CloudDataBucketPresignedUploadRequest.  # noqa: E501
        :rtype: str
        """
        return self._file_name

    @file_name.setter
    def file_name(self, file_name):
        """Sets the file_name of this CloudDataBucketPresignedUploadRequest.

        The name of the file that will be uploaded (e.g. 'runtime_env_1234.zip').  # noqa: E501

        :param file_name: The file_name of this CloudDataBucketPresignedUploadRequest.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and file_name is None:  # noqa: E501
            raise ValueError("Invalid value for `file_name`, must not be `None`")  # noqa: E501

        self._file_name = file_name

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
        if not isinstance(other, CloudDataBucketPresignedUploadRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CloudDataBucketPresignedUploadRequest):
            return True

        return self.to_dict() != other.to_dict()
