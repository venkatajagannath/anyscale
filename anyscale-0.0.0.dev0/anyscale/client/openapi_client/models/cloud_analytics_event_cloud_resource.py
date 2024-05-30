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


class CloudAnalyticsEventCloudResource(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    allowed enum values
    """
    UNSPECIFIED = "UNSPECIFIED"
    AWS_VPC = "AWS_VPC"
    AWS_SUBNET = "AWS_SUBNET"
    AWS_SECURITY_GROUP = "AWS_SECURITY_GROUP"
    AWS_S3_BUCKET = "AWS_S3_BUCKET"
    AWS_IAM_ROLE = "AWS_IAM_ROLE"
    AWS_EFS = "AWS_EFS"
    AWS_CLOUDFORMATION = "AWS_CLOUDFORMATION"
    AWS_MEMORYDB = "AWS_MEMORYDB"
    GCP_PROJECT = "GCP_PROJECT"
    GCP_VPC = "GCP_VPC"
    GCP_SUBNET = "GCP_SUBNET"
    GCP_SERVICE_ACCOUNT = "GCP_SERVICE_ACCOUNT"
    GCP_WORKLOAD_IDENTITY_PROVIDER = "GCP_WORKLOAD_IDENTITY_PROVIDER"
    GCP_FIREWALL_POLICY = "GCP_FIREWALL_POLICY"
    GCP_FILESTORE = "GCP_FILESTORE"
    GCP_STORAGE_BUCKET = "GCP_STORAGE_BUCKET"
    GCP_DEPLOYMENT = "GCP_DEPLOYMENT"
    GCP_MEMORYSTORE = "GCP_MEMORYSTORE"

    allowable_values = [UNSPECIFIED, AWS_VPC, AWS_SUBNET, AWS_SECURITY_GROUP, AWS_S3_BUCKET, AWS_IAM_ROLE, AWS_EFS, AWS_CLOUDFORMATION, AWS_MEMORYDB, GCP_PROJECT, GCP_VPC, GCP_SUBNET, GCP_SERVICE_ACCOUNT, GCP_WORKLOAD_IDENTITY_PROVIDER, GCP_FIREWALL_POLICY, GCP_FILESTORE, GCP_STORAGE_BUCKET, GCP_DEPLOYMENT, GCP_MEMORYSTORE]  # noqa: E501

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
    }

    attribute_map = {
    }

    def __init__(self, local_vars_configuration=None):  # noqa: E501
        """CloudAnalyticsEventCloudResource - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration
        self.discriminator = None

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
        if not isinstance(other, CloudAnalyticsEventCloudResource):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CloudAnalyticsEventCloudResource):
            return True

        return self.to_dict() != other.to_dict()
