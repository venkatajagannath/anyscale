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


class SessionCommandFinishOptions(object):
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
        'status_code': 'int',
        'stop': 'bool',
        'terminate': 'bool',
        'finished_at': 'datetime',
        'killed_at': 'datetime'
    }

    attribute_map = {
        'status_code': 'status_code',
        'stop': 'stop',
        'terminate': 'terminate',
        'finished_at': 'finished_at',
        'killed_at': 'killed_at'
    }

    def __init__(self, status_code=None, stop=None, terminate=False, finished_at=None, killed_at=None, local_vars_configuration=None):  # noqa: E501
        """SessionCommandFinishOptions - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._status_code = None
        self._stop = None
        self._terminate = None
        self._finished_at = None
        self._killed_at = None
        self.discriminator = None

        self.status_code = status_code
        self.stop = stop
        if terminate is not None:
            self.terminate = terminate
        if finished_at is not None:
            self.finished_at = finished_at
        if killed_at is not None:
            self.killed_at = killed_at

    @property
    def status_code(self):
        """Gets the status_code of this SessionCommandFinishOptions.  # noqa: E501


        :return: The status_code of this SessionCommandFinishOptions.  # noqa: E501
        :rtype: int
        """
        return self._status_code

    @status_code.setter
    def status_code(self, status_code):
        """Sets the status_code of this SessionCommandFinishOptions.


        :param status_code: The status_code of this SessionCommandFinishOptions.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and status_code is None:  # noqa: E501
            raise ValueError("Invalid value for `status_code`, must not be `None`")  # noqa: E501

        self._status_code = status_code

    @property
    def stop(self):
        """Gets the stop of this SessionCommandFinishOptions.  # noqa: E501


        :return: The stop of this SessionCommandFinishOptions.  # noqa: E501
        :rtype: bool
        """
        return self._stop

    @stop.setter
    def stop(self, stop):
        """Sets the stop of this SessionCommandFinishOptions.


        :param stop: The stop of this SessionCommandFinishOptions.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and stop is None:  # noqa: E501
            raise ValueError("Invalid value for `stop`, must not be `None`")  # noqa: E501

        self._stop = stop

    @property
    def terminate(self):
        """Gets the terminate of this SessionCommandFinishOptions.  # noqa: E501


        :return: The terminate of this SessionCommandFinishOptions.  # noqa: E501
        :rtype: bool
        """
        return self._terminate

    @terminate.setter
    def terminate(self, terminate):
        """Sets the terminate of this SessionCommandFinishOptions.


        :param terminate: The terminate of this SessionCommandFinishOptions.  # noqa: E501
        :type: bool
        """

        self._terminate = terminate

    @property
    def finished_at(self):
        """Gets the finished_at of this SessionCommandFinishOptions.  # noqa: E501


        :return: The finished_at of this SessionCommandFinishOptions.  # noqa: E501
        :rtype: datetime
        """
        return self._finished_at

    @finished_at.setter
    def finished_at(self, finished_at):
        """Sets the finished_at of this SessionCommandFinishOptions.


        :param finished_at: The finished_at of this SessionCommandFinishOptions.  # noqa: E501
        :type: datetime
        """

        self._finished_at = finished_at

    @property
    def killed_at(self):
        """Gets the killed_at of this SessionCommandFinishOptions.  # noqa: E501


        :return: The killed_at of this SessionCommandFinishOptions.  # noqa: E501
        :rtype: datetime
        """
        return self._killed_at

    @killed_at.setter
    def killed_at(self, killed_at):
        """Sets the killed_at of this SessionCommandFinishOptions.


        :param killed_at: The killed_at of this SessionCommandFinishOptions.  # noqa: E501
        :type: datetime
        """

        self._killed_at = killed_at

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
        if not isinstance(other, SessionCommandFinishOptions):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SessionCommandFinishOptions):
            return True

        return self.to_dict() != other.to_dict()
