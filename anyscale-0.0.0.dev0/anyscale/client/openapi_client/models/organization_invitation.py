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


class OrganizationInvitation(object):
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
        'email': 'str',
        'id': 'str',
        'organization_id': 'str',
        'accepted_at': 'datetime',
        'created_at': 'datetime',
        'expires_at': 'datetime'
    }

    attribute_map = {
        'email': 'email',
        'id': 'id',
        'organization_id': 'organization_id',
        'accepted_at': 'accepted_at',
        'created_at': 'created_at',
        'expires_at': 'expires_at'
    }

    def __init__(self, email=None, id=None, organization_id=None, accepted_at=None, created_at=None, expires_at=None, local_vars_configuration=None):  # noqa: E501
        """OrganizationInvitation - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._email = None
        self._id = None
        self._organization_id = None
        self._accepted_at = None
        self._created_at = None
        self._expires_at = None
        self.discriminator = None

        self.email = email
        self.id = id
        self.organization_id = organization_id
        if accepted_at is not None:
            self.accepted_at = accepted_at
        self.created_at = created_at
        self.expires_at = expires_at

    @property
    def email(self):
        """Gets the email of this OrganizationInvitation.  # noqa: E501


        :return: The email of this OrganizationInvitation.  # noqa: E501
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """Sets the email of this OrganizationInvitation.


        :param email: The email of this OrganizationInvitation.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and email is None:  # noqa: E501
            raise ValueError("Invalid value for `email`, must not be `None`")  # noqa: E501

        self._email = email

    @property
    def id(self):
        """Gets the id of this OrganizationInvitation.  # noqa: E501


        :return: The id of this OrganizationInvitation.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this OrganizationInvitation.


        :param id: The id of this OrganizationInvitation.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def organization_id(self):
        """Gets the organization_id of this OrganizationInvitation.  # noqa: E501


        :return: The organization_id of this OrganizationInvitation.  # noqa: E501
        :rtype: str
        """
        return self._organization_id

    @organization_id.setter
    def organization_id(self, organization_id):
        """Sets the organization_id of this OrganizationInvitation.


        :param organization_id: The organization_id of this OrganizationInvitation.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and organization_id is None:  # noqa: E501
            raise ValueError("Invalid value for `organization_id`, must not be `None`")  # noqa: E501

        self._organization_id = organization_id

    @property
    def accepted_at(self):
        """Gets the accepted_at of this OrganizationInvitation.  # noqa: E501


        :return: The accepted_at of this OrganizationInvitation.  # noqa: E501
        :rtype: datetime
        """
        return self._accepted_at

    @accepted_at.setter
    def accepted_at(self, accepted_at):
        """Sets the accepted_at of this OrganizationInvitation.


        :param accepted_at: The accepted_at of this OrganizationInvitation.  # noqa: E501
        :type: datetime
        """

        self._accepted_at = accepted_at

    @property
    def created_at(self):
        """Gets the created_at of this OrganizationInvitation.  # noqa: E501


        :return: The created_at of this OrganizationInvitation.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this OrganizationInvitation.


        :param created_at: The created_at of this OrganizationInvitation.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and created_at is None:  # noqa: E501
            raise ValueError("Invalid value for `created_at`, must not be `None`")  # noqa: E501

        self._created_at = created_at

    @property
    def expires_at(self):
        """Gets the expires_at of this OrganizationInvitation.  # noqa: E501


        :return: The expires_at of this OrganizationInvitation.  # noqa: E501
        :rtype: datetime
        """
        return self._expires_at

    @expires_at.setter
    def expires_at(self, expires_at):
        """Sets the expires_at of this OrganizationInvitation.


        :param expires_at: The expires_at of this OrganizationInvitation.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and expires_at is None:  # noqa: E501
            raise ValueError("Invalid value for `expires_at`, must not be `None`")  # noqa: E501

        self._expires_at = expires_at

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
        if not isinstance(other, OrganizationInvitation):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, OrganizationInvitation):
            return True

        return self.to_dict() != other.to_dict()
