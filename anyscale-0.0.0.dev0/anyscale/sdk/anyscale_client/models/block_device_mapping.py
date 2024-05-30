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


class BlockDeviceMapping(object):
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
        'device_name': 'str',
        'ebs': 'EbsBlockDevice',
        'no_device': 'str',
        'virtual_name': 'str'
    }

    attribute_map = {
        'device_name': 'DeviceName',
        'ebs': 'Ebs',
        'no_device': 'NoDevice',
        'virtual_name': 'VirtualName'
    }

    def __init__(self, device_name=None, ebs=None, no_device=None, virtual_name=None, local_vars_configuration=None):  # noqa: E501
        """BlockDeviceMapping - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._device_name = None
        self._ebs = None
        self._no_device = None
        self._virtual_name = None
        self.discriminator = None

        if device_name is not None:
            self.device_name = device_name
        if ebs is not None:
            self.ebs = ebs
        if no_device is not None:
            self.no_device = no_device
        if virtual_name is not None:
            self.virtual_name = virtual_name

    @property
    def device_name(self):
        """Gets the device_name of this BlockDeviceMapping.  # noqa: E501


        :return: The device_name of this BlockDeviceMapping.  # noqa: E501
        :rtype: str
        """
        return self._device_name

    @device_name.setter
    def device_name(self, device_name):
        """Sets the device_name of this BlockDeviceMapping.


        :param device_name: The device_name of this BlockDeviceMapping.  # noqa: E501
        :type: str
        """

        self._device_name = device_name

    @property
    def ebs(self):
        """Gets the ebs of this BlockDeviceMapping.  # noqa: E501


        :return: The ebs of this BlockDeviceMapping.  # noqa: E501
        :rtype: EbsBlockDevice
        """
        return self._ebs

    @ebs.setter
    def ebs(self, ebs):
        """Sets the ebs of this BlockDeviceMapping.


        :param ebs: The ebs of this BlockDeviceMapping.  # noqa: E501
        :type: EbsBlockDevice
        """

        self._ebs = ebs

    @property
    def no_device(self):
        """Gets the no_device of this BlockDeviceMapping.  # noqa: E501


        :return: The no_device of this BlockDeviceMapping.  # noqa: E501
        :rtype: str
        """
        return self._no_device

    @no_device.setter
    def no_device(self, no_device):
        """Sets the no_device of this BlockDeviceMapping.


        :param no_device: The no_device of this BlockDeviceMapping.  # noqa: E501
        :type: str
        """

        self._no_device = no_device

    @property
    def virtual_name(self):
        """Gets the virtual_name of this BlockDeviceMapping.  # noqa: E501


        :return: The virtual_name of this BlockDeviceMapping.  # noqa: E501
        :rtype: str
        """
        return self._virtual_name

    @virtual_name.setter
    def virtual_name(self, virtual_name):
        """Sets the virtual_name of this BlockDeviceMapping.


        :param virtual_name: The virtual_name of this BlockDeviceMapping.  # noqa: E501
        :type: str
        """

        self._virtual_name = virtual_name

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
        if not isinstance(other, BlockDeviceMapping):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, BlockDeviceMapping):
            return True

        return self.to_dict() != other.to_dict()
