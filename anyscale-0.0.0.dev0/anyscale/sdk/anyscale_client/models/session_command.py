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


class SessionCommand(object):
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
        'session_id': 'str',
        'shell_command': 'str',
        'id': 'str',
        'type': 'SessionCommandTypes',
        'created_at': 'datetime',
        'finished_at': 'datetime',
        'status_code': 'int',
        'killed_at': 'datetime',
        'web_terminal_tab_id': 'str'
    }

    attribute_map = {
        'session_id': 'session_id',
        'shell_command': 'shell_command',
        'id': 'id',
        'type': 'type',
        'created_at': 'created_at',
        'finished_at': 'finished_at',
        'status_code': 'status_code',
        'killed_at': 'killed_at',
        'web_terminal_tab_id': 'web_terminal_tab_id'
    }

    def __init__(self, session_id=None, shell_command=None, id=None, type=None, created_at=None, finished_at=None, status_code=None, killed_at=None, web_terminal_tab_id=None, local_vars_configuration=None):  # noqa: E501
        """SessionCommand - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._session_id = None
        self._shell_command = None
        self._id = None
        self._type = None
        self._created_at = None
        self._finished_at = None
        self._status_code = None
        self._killed_at = None
        self._web_terminal_tab_id = None
        self.discriminator = None

        self.session_id = session_id
        self.shell_command = shell_command
        self.id = id
        if type is not None:
            self.type = type
        self.created_at = created_at
        if finished_at is not None:
            self.finished_at = finished_at
        if status_code is not None:
            self.status_code = status_code
        if killed_at is not None:
            self.killed_at = killed_at
        if web_terminal_tab_id is not None:
            self.web_terminal_tab_id = web_terminal_tab_id

    @property
    def session_id(self):
        """Gets the session_id of this SessionCommand.  # noqa: E501

        ID of the Session to execute this command on.  # noqa: E501

        :return: The session_id of this SessionCommand.  # noqa: E501
        :rtype: str
        """
        return self._session_id

    @session_id.setter
    def session_id(self, session_id):
        """Sets the session_id of this SessionCommand.

        ID of the Session to execute this command on.  # noqa: E501

        :param session_id: The session_id of this SessionCommand.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and session_id is None:  # noqa: E501
            raise ValueError("Invalid value for `session_id`, must not be `None`")  # noqa: E501

        self._session_id = session_id

    @property
    def shell_command(self):
        """Gets the shell_command of this SessionCommand.  # noqa: E501

        Shell command string that will be executed.  # noqa: E501

        :return: The shell_command of this SessionCommand.  # noqa: E501
        :rtype: str
        """
        return self._shell_command

    @shell_command.setter
    def shell_command(self, shell_command):
        """Sets the shell_command of this SessionCommand.

        Shell command string that will be executed.  # noqa: E501

        :param shell_command: The shell_command of this SessionCommand.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and shell_command is None:  # noqa: E501
            raise ValueError("Invalid value for `shell_command`, must not be `None`")  # noqa: E501

        self._shell_command = shell_command

    @property
    def id(self):
        """Gets the id of this SessionCommand.  # noqa: E501

        Server assigned unique identifier.  # noqa: E501

        :return: The id of this SessionCommand.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this SessionCommand.

        Server assigned unique identifier.  # noqa: E501

        :param id: The id of this SessionCommand.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def type(self):
        """Gets the type of this SessionCommand.  # noqa: E501

        Where this command was executed  # noqa: E501

        :return: The type of this SessionCommand.  # noqa: E501
        :rtype: SessionCommandTypes
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this SessionCommand.

        Where this command was executed  # noqa: E501

        :param type: The type of this SessionCommand.  # noqa: E501
        :type: SessionCommandTypes
        """

        self._type = type

    @property
    def created_at(self):
        """Gets the created_at of this SessionCommand.  # noqa: E501

        Timestamp of when this command was created.  # noqa: E501

        :return: The created_at of this SessionCommand.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this SessionCommand.

        Timestamp of when this command was created.  # noqa: E501

        :param created_at: The created_at of this SessionCommand.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and created_at is None:  # noqa: E501
            raise ValueError("Invalid value for `created_at`, must not be `None`")  # noqa: E501

        self._created_at = created_at

    @property
    def finished_at(self):
        """Gets the finished_at of this SessionCommand.  # noqa: E501

                 Timestamp of when this command completed its execution.         This value will be absent if the command is still running.           # noqa: E501

        :return: The finished_at of this SessionCommand.  # noqa: E501
        :rtype: datetime
        """
        return self._finished_at

    @finished_at.setter
    def finished_at(self, finished_at):
        """Sets the finished_at of this SessionCommand.

                 Timestamp of when this command completed its execution.         This value will be absent if the command is still running.           # noqa: E501

        :param finished_at: The finished_at of this SessionCommand.  # noqa: E501
        :type: datetime
        """

        self._finished_at = finished_at

    @property
    def status_code(self):
        """Gets the status_code of this SessionCommand.  # noqa: E501

                 Exit status of this command.         This value will be absent if the command is still running.           # noqa: E501

        :return: The status_code of this SessionCommand.  # noqa: E501
        :rtype: int
        """
        return self._status_code

    @status_code.setter
    def status_code(self, status_code):
        """Sets the status_code of this SessionCommand.

                 Exit status of this command.         This value will be absent if the command is still running.           # noqa: E501

        :param status_code: The status_code of this SessionCommand.  # noqa: E501
        :type: int
        """

        self._status_code = status_code

    @property
    def killed_at(self):
        """Gets the killed_at of this SessionCommand.  # noqa: E501

                 Timestamp of when this command was killed.         This value will be absent if the command is still running or completed its execution normally.           # noqa: E501

        :return: The killed_at of this SessionCommand.  # noqa: E501
        :rtype: datetime
        """
        return self._killed_at

    @killed_at.setter
    def killed_at(self, killed_at):
        """Sets the killed_at of this SessionCommand.

                 Timestamp of when this command was killed.         This value will be absent if the command is still running or completed its execution normally.           # noqa: E501

        :param killed_at: The killed_at of this SessionCommand.  # noqa: E501
        :type: datetime
        """

        self._killed_at = killed_at

    @property
    def web_terminal_tab_id(self):
        """Gets the web_terminal_tab_id of this SessionCommand.  # noqa: E501

                 The id for the web terminal tab in which this         command was executed.           # noqa: E501

        :return: The web_terminal_tab_id of this SessionCommand.  # noqa: E501
        :rtype: str
        """
        return self._web_terminal_tab_id

    @web_terminal_tab_id.setter
    def web_terminal_tab_id(self, web_terminal_tab_id):
        """Sets the web_terminal_tab_id of this SessionCommand.

                 The id for the web terminal tab in which this         command was executed.           # noqa: E501

        :param web_terminal_tab_id: The web_terminal_tab_id of this SessionCommand.  # noqa: E501
        :type: str
        """

        self._web_terminal_tab_id = web_terminal_tab_id

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
        if not isinstance(other, SessionCommand):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, SessionCommand):
            return True

        return self.to_dict() != other.to_dict()
