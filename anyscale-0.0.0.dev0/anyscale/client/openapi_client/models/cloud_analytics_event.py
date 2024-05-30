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


class CloudAnalyticsEvent(object):
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
        'trace_id': 'str',
        'cloud_id': 'str',
        'succeeded': 'bool',
        'command_name': 'CloudAnalyticsEventCommandName',
        'raw_command_input': 'str',
        'event_name': 'CloudAnalyticsEventName',
        'error': 'CloudAnalyticsEventError',
        'cloud_provider': 'CloudProviders',
        'cli_version': 'str'
    }

    attribute_map = {
        'trace_id': 'trace_id',
        'cloud_id': 'cloud_id',
        'succeeded': 'succeeded',
        'command_name': 'command_name',
        'raw_command_input': 'raw_command_input',
        'event_name': 'event_name',
        'error': 'error',
        'cloud_provider': 'cloud_provider',
        'cli_version': 'cli_version'
    }

    def __init__(self, trace_id=None, cloud_id=None, succeeded=None, command_name=None, raw_command_input=None, event_name=None, error=None, cloud_provider=None, cli_version=None, local_vars_configuration=None):  # noqa: E501
        """CloudAnalyticsEvent - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._trace_id = None
        self._cloud_id = None
        self._succeeded = None
        self._command_name = None
        self._raw_command_input = None
        self._event_name = None
        self._error = None
        self._cloud_provider = None
        self._cli_version = None
        self.discriminator = None

        self.trace_id = trace_id
        if cloud_id is not None:
            self.cloud_id = cloud_id
        self.succeeded = succeeded
        self.command_name = command_name
        self.raw_command_input = raw_command_input
        self.event_name = event_name
        if error is not None:
            self.error = error
        if cloud_provider is not None:
            self.cloud_provider = cloud_provider
        if cli_version is not None:
            self.cli_version = cli_version

    @property
    def trace_id(self):
        """Gets the trace_id of this CloudAnalyticsEvent.  # noqa: E501

        The trace id generated by CLI  # noqa: E501

        :return: The trace_id of this CloudAnalyticsEvent.  # noqa: E501
        :rtype: str
        """
        return self._trace_id

    @trace_id.setter
    def trace_id(self, trace_id):
        """Sets the trace_id of this CloudAnalyticsEvent.

        The trace id generated by CLI  # noqa: E501

        :param trace_id: The trace_id of this CloudAnalyticsEvent.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and trace_id is None:  # noqa: E501
            raise ValueError("Invalid value for `trace_id`, must not be `None`")  # noqa: E501

        self._trace_id = trace_id

    @property
    def cloud_id(self):
        """Gets the cloud_id of this CloudAnalyticsEvent.  # noqa: E501

        The cloud id  # noqa: E501

        :return: The cloud_id of this CloudAnalyticsEvent.  # noqa: E501
        :rtype: str
        """
        return self._cloud_id

    @cloud_id.setter
    def cloud_id(self, cloud_id):
        """Sets the cloud_id of this CloudAnalyticsEvent.

        The cloud id  # noqa: E501

        :param cloud_id: The cloud_id of this CloudAnalyticsEvent.  # noqa: E501
        :type: str
        """

        self._cloud_id = cloud_id

    @property
    def succeeded(self):
        """Gets the succeeded of this CloudAnalyticsEvent.  # noqa: E501

        Whether the operation succeeded  # noqa: E501

        :return: The succeeded of this CloudAnalyticsEvent.  # noqa: E501
        :rtype: bool
        """
        return self._succeeded

    @succeeded.setter
    def succeeded(self, succeeded):
        """Sets the succeeded of this CloudAnalyticsEvent.

        Whether the operation succeeded  # noqa: E501

        :param succeeded: The succeeded of this CloudAnalyticsEvent.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and succeeded is None:  # noqa: E501
            raise ValueError("Invalid value for `succeeded`, must not be `None`")  # noqa: E501

        self._succeeded = succeeded

    @property
    def command_name(self):
        """Gets the command_name of this CloudAnalyticsEvent.  # noqa: E501

        The command name (e.g. setup, register)  # noqa: E501

        :return: The command_name of this CloudAnalyticsEvent.  # noqa: E501
        :rtype: CloudAnalyticsEventCommandName
        """
        return self._command_name

    @command_name.setter
    def command_name(self, command_name):
        """Sets the command_name of this CloudAnalyticsEvent.

        The command name (e.g. setup, register)  # noqa: E501

        :param command_name: The command_name of this CloudAnalyticsEvent.  # noqa: E501
        :type: CloudAnalyticsEventCommandName
        """
        if self.local_vars_configuration.client_side_validation and command_name is None:  # noqa: E501
            raise ValueError("Invalid value for `command_name`, must not be `None`")  # noqa: E501

        self._command_name = command_name

    @property
    def raw_command_input(self):
        """Gets the raw_command_input of this CloudAnalyticsEvent.  # noqa: E501

        The command from user input (e.g. 'cloud verify my_cloud')  # noqa: E501

        :return: The raw_command_input of this CloudAnalyticsEvent.  # noqa: E501
        :rtype: str
        """
        return self._raw_command_input

    @raw_command_input.setter
    def raw_command_input(self, raw_command_input):
        """Sets the raw_command_input of this CloudAnalyticsEvent.

        The command from user input (e.g. 'cloud verify my_cloud')  # noqa: E501

        :param raw_command_input: The raw_command_input of this CloudAnalyticsEvent.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and raw_command_input is None:  # noqa: E501
            raise ValueError("Invalid value for `raw_command_input`, must not be `None`")  # noqa: E501

        self._raw_command_input = raw_command_input

    @property
    def event_name(self):
        """Gets the event_name of this CloudAnalyticsEvent.  # noqa: E501

        The event name (e.g. command_start, resources_created)  # noqa: E501

        :return: The event_name of this CloudAnalyticsEvent.  # noqa: E501
        :rtype: CloudAnalyticsEventName
        """
        return self._event_name

    @event_name.setter
    def event_name(self, event_name):
        """Sets the event_name of this CloudAnalyticsEvent.

        The event name (e.g. command_start, resources_created)  # noqa: E501

        :param event_name: The event_name of this CloudAnalyticsEvent.  # noqa: E501
        :type: CloudAnalyticsEventName
        """
        if self.local_vars_configuration.client_side_validation and event_name is None:  # noqa: E501
            raise ValueError("Invalid value for `event_name`, must not be `None`")  # noqa: E501

        self._event_name = event_name

    @property
    def error(self):
        """Gets the error of this CloudAnalyticsEvent.  # noqa: E501

        The error. It is only populated when succeeded is false.  # noqa: E501

        :return: The error of this CloudAnalyticsEvent.  # noqa: E501
        :rtype: CloudAnalyticsEventError
        """
        return self._error

    @error.setter
    def error(self, error):
        """Sets the error of this CloudAnalyticsEvent.

        The error. It is only populated when succeeded is false.  # noqa: E501

        :param error: The error of this CloudAnalyticsEvent.  # noqa: E501
        :type: CloudAnalyticsEventError
        """

        self._error = error

    @property
    def cloud_provider(self):
        """Gets the cloud_provider of this CloudAnalyticsEvent.  # noqa: E501

        The cloud provider (e.g. AWS, GCP)  # noqa: E501

        :return: The cloud_provider of this CloudAnalyticsEvent.  # noqa: E501
        :rtype: CloudProviders
        """
        return self._cloud_provider

    @cloud_provider.setter
    def cloud_provider(self, cloud_provider):
        """Sets the cloud_provider of this CloudAnalyticsEvent.

        The cloud provider (e.g. AWS, GCP)  # noqa: E501

        :param cloud_provider: The cloud_provider of this CloudAnalyticsEvent.  # noqa: E501
        :type: CloudProviders
        """

        self._cloud_provider = cloud_provider

    @property
    def cli_version(self):
        """Gets the cli_version of this CloudAnalyticsEvent.  # noqa: E501

        The CLI version  # noqa: E501

        :return: The cli_version of this CloudAnalyticsEvent.  # noqa: E501
        :rtype: str
        """
        return self._cli_version

    @cli_version.setter
    def cli_version(self, cli_version):
        """Sets the cli_version of this CloudAnalyticsEvent.

        The CLI version  # noqa: E501

        :param cli_version: The cli_version of this CloudAnalyticsEvent.  # noqa: E501
        :type: str
        """

        self._cli_version = cli_version

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
        if not isinstance(other, CloudAnalyticsEvent):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CloudAnalyticsEvent):
            return True

        return self.to_dict() != other.to_dict()
