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


class StopSessionOptions(object):
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
        'terminate': 'bool',
        'workers_only': 'bool',
        'keep_min_workers': 'bool',
        'delete': 'bool',
        'take_snapshot': 'bool'
    }

    attribute_map = {
        'terminate': 'terminate',
        'workers_only': 'workers_only',
        'keep_min_workers': 'keep_min_workers',
        'delete': 'delete',
        'take_snapshot': 'take_snapshot'
    }

    def __init__(self, terminate=None, workers_only=None, keep_min_workers=None, delete=False, take_snapshot=False, local_vars_configuration=None):  # noqa: E501
        """StopSessionOptions - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._terminate = None
        self._workers_only = None
        self._keep_min_workers = None
        self._delete = None
        self._take_snapshot = None
        self.discriminator = None

        self.terminate = terminate
        self.workers_only = workers_only
        self.keep_min_workers = keep_min_workers
        if delete is not None:
            self.delete = delete
        if take_snapshot is not None:
            self.take_snapshot = take_snapshot

    @property
    def terminate(self):
        """Gets the terminate of this StopSessionOptions.  # noqa: E501


        :return: The terminate of this StopSessionOptions.  # noqa: E501
        :rtype: bool
        """
        return self._terminate

    @terminate.setter
    def terminate(self, terminate):
        """Sets the terminate of this StopSessionOptions.


        :param terminate: The terminate of this StopSessionOptions.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and terminate is None:  # noqa: E501
            raise ValueError("Invalid value for `terminate`, must not be `None`")  # noqa: E501

        self._terminate = terminate

    @property
    def workers_only(self):
        """Gets the workers_only of this StopSessionOptions.  # noqa: E501


        :return: The workers_only of this StopSessionOptions.  # noqa: E501
        :rtype: bool
        """
        return self._workers_only

    @workers_only.setter
    def workers_only(self, workers_only):
        """Sets the workers_only of this StopSessionOptions.


        :param workers_only: The workers_only of this StopSessionOptions.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and workers_only is None:  # noqa: E501
            raise ValueError("Invalid value for `workers_only`, must not be `None`")  # noqa: E501

        self._workers_only = workers_only

    @property
    def keep_min_workers(self):
        """Gets the keep_min_workers of this StopSessionOptions.  # noqa: E501


        :return: The keep_min_workers of this StopSessionOptions.  # noqa: E501
        :rtype: bool
        """
        return self._keep_min_workers

    @keep_min_workers.setter
    def keep_min_workers(self, keep_min_workers):
        """Sets the keep_min_workers of this StopSessionOptions.


        :param keep_min_workers: The keep_min_workers of this StopSessionOptions.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and keep_min_workers is None:  # noqa: E501
            raise ValueError("Invalid value for `keep_min_workers`, must not be `None`")  # noqa: E501

        self._keep_min_workers = keep_min_workers

    @property
    def delete(self):
        """Gets the delete of this StopSessionOptions.  # noqa: E501


        :return: The delete of this StopSessionOptions.  # noqa: E501
        :rtype: bool
        """
        return self._delete

    @delete.setter
    def delete(self, delete):
        """Sets the delete of this StopSessionOptions.


        :param delete: The delete of this StopSessionOptions.  # noqa: E501
        :type: bool
        """

        self._delete = delete

    @property
    def take_snapshot(self):
        """Gets the take_snapshot of this StopSessionOptions.  # noqa: E501


        :return: The take_snapshot of this StopSessionOptions.  # noqa: E501
        :rtype: bool
        """
        return self._take_snapshot

    @take_snapshot.setter
    def take_snapshot(self, take_snapshot):
        """Sets the take_snapshot of this StopSessionOptions.


        :param take_snapshot: The take_snapshot of this StopSessionOptions.  # noqa: E501
        :type: bool
        """

        self._take_snapshot = take_snapshot

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
        if not isinstance(other, StopSessionOptions):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, StopSessionOptions):
            return True

        return self.to_dict() != other.to_dict()
