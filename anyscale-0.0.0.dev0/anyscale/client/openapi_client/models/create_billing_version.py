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


class CreateBillingVersion(object):
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
        'organization_id': 'str',
        'version': 'BillingVersionCode',
        'effective_date': 'datetime'
    }

    attribute_map = {
        'organization_id': 'organization_id',
        'version': 'version',
        'effective_date': 'effective_date'
    }

    def __init__(self, organization_id=None, version=None, effective_date=None, local_vars_configuration=None):  # noqa: E501
        """CreateBillingVersion - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._organization_id = None
        self._version = None
        self._effective_date = None
        self.discriminator = None

        self.organization_id = organization_id
        self.version = version
        self.effective_date = effective_date

    @property
    def organization_id(self):
        """Gets the organization_id of this CreateBillingVersion.  # noqa: E501

        The organization ID to be assigned the billing version.  # noqa: E501

        :return: The organization_id of this CreateBillingVersion.  # noqa: E501
        :rtype: str
        """
        return self._organization_id

    @organization_id.setter
    def organization_id(self, organization_id):
        """Sets the organization_id of this CreateBillingVersion.

        The organization ID to be assigned the billing version.  # noqa: E501

        :param organization_id: The organization_id of this CreateBillingVersion.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and organization_id is None:  # noqa: E501
            raise ValueError("Invalid value for `organization_id`, must not be `None`")  # noqa: E501

        self._organization_id = organization_id

    @property
    def version(self):
        """Gets the version of this CreateBillingVersion.  # noqa: E501

        The billing version to be assigned to the organization.  # noqa: E501

        :return: The version of this CreateBillingVersion.  # noqa: E501
        :rtype: BillingVersionCode
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this CreateBillingVersion.

        The billing version to be assigned to the organization.  # noqa: E501

        :param version: The version of this CreateBillingVersion.  # noqa: E501
        :type: BillingVersionCode
        """
        if self.local_vars_configuration.client_side_validation and version is None:  # noqa: E501
            raise ValueError("Invalid value for `version`, must not be `None`")  # noqa: E501

        self._version = version

    @property
    def effective_date(self):
        """Gets the effective_date of this CreateBillingVersion.  # noqa: E501

        The date when the billing version will take effect. If an organization has multiple billing versions, the one with the latest effective date that is not in the future will be used.To avoid inconsistencies, this value should always be scheduled to take effect in the future.  # noqa: E501

        :return: The effective_date of this CreateBillingVersion.  # noqa: E501
        :rtype: datetime
        """
        return self._effective_date

    @effective_date.setter
    def effective_date(self, effective_date):
        """Sets the effective_date of this CreateBillingVersion.

        The date when the billing version will take effect. If an organization has multiple billing versions, the one with the latest effective date that is not in the future will be used.To avoid inconsistencies, this value should always be scheduled to take effect in the future.  # noqa: E501

        :param effective_date: The effective_date of this CreateBillingVersion.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and effective_date is None:  # noqa: E501
            raise ValueError("Invalid value for `effective_date`, must not be `None`")  # noqa: E501

        self._effective_date = effective_date

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
        if not isinstance(other, CreateBillingVersion):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateBillingVersion):
            return True

        return self.to_dict() != other.to_dict()
