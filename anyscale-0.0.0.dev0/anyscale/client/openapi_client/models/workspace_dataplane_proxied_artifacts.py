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


class WorkspaceDataplaneProxiedArtifacts(object):
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
        'requirements': 'str',
        'skip_packages_tracking': 'str',
        'environment_variables': 'list[str]'
    }

    attribute_map = {
        'requirements': 'requirements',
        'skip_packages_tracking': 'skip_packages_tracking',
        'environment_variables': 'environment_variables'
    }

    def __init__(self, requirements=None, skip_packages_tracking=None, environment_variables=None, local_vars_configuration=None):  # noqa: E501
        """WorkspaceDataplaneProxiedArtifacts - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._requirements = None
        self._skip_packages_tracking = None
        self._environment_variables = None
        self.discriminator = None

        if requirements is not None:
            self.requirements = requirements
        if skip_packages_tracking is not None:
            self.skip_packages_tracking = skip_packages_tracking
        if environment_variables is not None:
            self.environment_variables = environment_variables

    @property
    def requirements(self):
        """Gets the requirements of this WorkspaceDataplaneProxiedArtifacts.  # noqa: E501

        The requirements.txt of the workspace.  # noqa: E501

        :return: The requirements of this WorkspaceDataplaneProxiedArtifacts.  # noqa: E501
        :rtype: str
        """
        return self._requirements

    @requirements.setter
    def requirements(self, requirements):
        """Sets the requirements of this WorkspaceDataplaneProxiedArtifacts.

        The requirements.txt of the workspace.  # noqa: E501

        :param requirements: The requirements of this WorkspaceDataplaneProxiedArtifacts.  # noqa: E501
        :type: str
        """

        self._requirements = requirements

    @property
    def skip_packages_tracking(self):
        """Gets the skip_packages_tracking of this WorkspaceDataplaneProxiedArtifacts.  # noqa: E501

        The .skip_packages_tracking of the workspace.  # noqa: E501

        :return: The skip_packages_tracking of this WorkspaceDataplaneProxiedArtifacts.  # noqa: E501
        :rtype: str
        """
        return self._skip_packages_tracking

    @skip_packages_tracking.setter
    def skip_packages_tracking(self, skip_packages_tracking):
        """Sets the skip_packages_tracking of this WorkspaceDataplaneProxiedArtifacts.

        The .skip_packages_tracking of the workspace.  # noqa: E501

        :param skip_packages_tracking: The skip_packages_tracking of this WorkspaceDataplaneProxiedArtifacts.  # noqa: E501
        :type: str
        """

        self._skip_packages_tracking = skip_packages_tracking

    @property
    def environment_variables(self):
        """Gets the environment_variables of this WorkspaceDataplaneProxiedArtifacts.  # noqa: E501

        The environment variables file of the workspace.  # noqa: E501

        :return: The environment_variables of this WorkspaceDataplaneProxiedArtifacts.  # noqa: E501
        :rtype: list[str]
        """
        return self._environment_variables

    @environment_variables.setter
    def environment_variables(self, environment_variables):
        """Sets the environment_variables of this WorkspaceDataplaneProxiedArtifacts.

        The environment variables file of the workspace.  # noqa: E501

        :param environment_variables: The environment_variables of this WorkspaceDataplaneProxiedArtifacts.  # noqa: E501
        :type: list[str]
        """

        self._environment_variables = environment_variables

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
        if not isinstance(other, WorkspaceDataplaneProxiedArtifacts):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, WorkspaceDataplaneProxiedArtifacts):
            return True

        return self.to_dict() != other.to_dict()
