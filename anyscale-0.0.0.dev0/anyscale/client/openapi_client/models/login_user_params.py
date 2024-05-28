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


class LoginUserParams(object):
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
        'password': 'str',
        'organization_id': 'str',
        'magic_token': 'str'
    }

    attribute_map = {
        'email': 'email',
        'password': 'password',
        'organization_id': 'organization_id',
        'magic_token': 'magic_token'
    }

    def __init__(self, email=None, password=None, organization_id=None, magic_token=None, local_vars_configuration=None):  # noqa: E501
        """LoginUserParams - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._email = None
        self._password = None
        self._organization_id = None
        self._magic_token = None
        self.discriminator = None

        self.email = email
        if password is not None:
            self.password = password
        if organization_id is not None:
            self.organization_id = organization_id
        if magic_token is not None:
            self.magic_token = magic_token

    @property
    def email(self):
        """Gets the email of this LoginUserParams.  # noqa: E501


        :return: The email of this LoginUserParams.  # noqa: E501
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """Sets the email of this LoginUserParams.


        :param email: The email of this LoginUserParams.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and email is None:  # noqa: E501
            raise ValueError("Invalid value for `email`, must not be `None`")  # noqa: E501

        self._email = email

    @property
    def password(self):
        """Gets the password of this LoginUserParams.  # noqa: E501

        Password to use for logging in as the user. At least one authentication method should be used. Either password or magic link.  # noqa: E501

        :return: The password of this LoginUserParams.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """Sets the password of this LoginUserParams.

        Password to use for logging in as the user. At least one authentication method should be used. Either password or magic link.  # noqa: E501

        :param password: The password of this LoginUserParams.  # noqa: E501
        :type: str
        """

        self._password = password

    @property
    def organization_id(self):
        """Gets the organization_id of this LoginUserParams.  # noqa: E501

        Specific organization to sign in to. If not provided, we default to the pre-multi-org user.  # noqa: E501

        :return: The organization_id of this LoginUserParams.  # noqa: E501
        :rtype: str
        """
        return self._organization_id

    @organization_id.setter
    def organization_id(self, organization_id):
        """Sets the organization_id of this LoginUserParams.

        Specific organization to sign in to. If not provided, we default to the pre-multi-org user.  # noqa: E501

        :param organization_id: The organization_id of this LoginUserParams.  # noqa: E501
        :type: str
        """

        self._organization_id = organization_id

    @property
    def magic_token(self):
        """Gets the magic_token of this LoginUserParams.  # noqa: E501

        Magic link token to authenticate ownership of an email address. At least one authentication method should be used. Either password or magic link.  # noqa: E501

        :return: The magic_token of this LoginUserParams.  # noqa: E501
        :rtype: str
        """
        return self._magic_token

    @magic_token.setter
    def magic_token(self, magic_token):
        """Sets the magic_token of this LoginUserParams.

        Magic link token to authenticate ownership of an email address. At least one authentication method should be used. Either password or magic link.  # noqa: E501

        :param magic_token: The magic_token of this LoginUserParams.  # noqa: E501
        :type: str
        """

        self._magic_token = magic_token

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
        if not isinstance(other, LoginUserParams):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, LoginUserParams):
            return True

        return self.to_dict() != other.to_dict()
