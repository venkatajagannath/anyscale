# coding: utf-8

"""
    Anyscale API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from anyscale_client.configuration import Configuration


class CreateComputeTemplate(object):
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
        'name': 'str',
        'project_id': 'str',
        'config': 'CreateComputeTemplateConfig',
        'anonymous': 'bool',
        'new_version': 'bool'
    }

    attribute_map = {
        'name': 'name',
        'project_id': 'project_id',
        'config': 'config',
        'anonymous': 'anonymous',
        'new_version': 'new_version'
    }

    def __init__(self, name=None, project_id=None, config=None, anonymous=False, new_version=False, local_vars_configuration=None):  # noqa: E501
        """CreateComputeTemplate - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self._project_id = None
        self._config = None
        self._anonymous = None
        self._new_version = None
        self.discriminator = None

        if name is not None:
            self.name = name
        if project_id is not None:
            self.project_id = project_id
        self.config = config
        if anonymous is not None:
            self.anonymous = anonymous
        if new_version is not None:
            self.new_version = new_version

    @property
    def name(self):
        """Gets the name of this CreateComputeTemplate.  # noqa: E501


        :return: The name of this CreateComputeTemplate.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this CreateComputeTemplate.


        :param name: The name of this CreateComputeTemplate.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def project_id(self):
        """Gets the project_id of this CreateComputeTemplate.  # noqa: E501


        :return: The project_id of this CreateComputeTemplate.  # noqa: E501
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this CreateComputeTemplate.


        :param project_id: The project_id of this CreateComputeTemplate.  # noqa: E501
        :type: str
        """

        self._project_id = project_id

    @property
    def config(self):
        """Gets the config of this CreateComputeTemplate.  # noqa: E501


        :return: The config of this CreateComputeTemplate.  # noqa: E501
        :rtype: CreateComputeTemplateConfig
        """
        return self._config

    @config.setter
    def config(self, config):
        """Sets the config of this CreateComputeTemplate.


        :param config: The config of this CreateComputeTemplate.  # noqa: E501
        :type: CreateComputeTemplateConfig
        """
        if self.local_vars_configuration.client_side_validation and config is None:  # noqa: E501
            raise ValueError("Invalid value for `config`, must not be `None`")  # noqa: E501

        self._config = config

    @property
    def anonymous(self):
        """Gets the anonymous of this CreateComputeTemplate.  # noqa: E501

        An anonymous cluster compute does not show up in the list of cluster configs. They can still have a name so they can be easily identified.  # noqa: E501

        :return: The anonymous of this CreateComputeTemplate.  # noqa: E501
        :rtype: bool
        """
        return self._anonymous

    @anonymous.setter
    def anonymous(self, anonymous):
        """Sets the anonymous of this CreateComputeTemplate.

        An anonymous cluster compute does not show up in the list of cluster configs. They can still have a name so they can be easily identified.  # noqa: E501

        :param anonymous: The anonymous of this CreateComputeTemplate.  # noqa: E501
        :type: bool
        """

        self._anonymous = anonymous

    @property
    def new_version(self):
        """Gets the new_version of this CreateComputeTemplate.  # noqa: E501

        If a Compute Template with the same name already exists, create this config as a new version.  # noqa: E501

        :return: The new_version of this CreateComputeTemplate.  # noqa: E501
        :rtype: bool
        """
        return self._new_version

    @new_version.setter
    def new_version(self, new_version):
        """Sets the new_version of this CreateComputeTemplate.

        If a Compute Template with the same name already exists, create this config as a new version.  # noqa: E501

        :param new_version: The new_version of this CreateComputeTemplate.  # noqa: E501
        :type: bool
        """

        self._new_version = new_version

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
        if not isinstance(other, CreateComputeTemplate):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateComputeTemplate):
            return True

        return self.to_dict() != other.to_dict()
