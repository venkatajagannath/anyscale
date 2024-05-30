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


class CreateSessionFromSnapshotOptions(object):
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
        'project_id': 'str',
        'name': 'str',
        'session_params': 'object',
        'command_name': 'str',
        'command_params': 'object',
        'shell': 'bool',
        'min_workers': 'int',
        'max_workers': 'int',
        'cluster_config': 'WriteClusterConfig',
        'build_id': 'str',
        'compute_template_id': 'str',
        'cloud_id': 'str',
        'start_session': 'bool',
        'wait_for_snapshot': 'bool',
        'idle_timeout': 'int',
        'uses_app_config': 'bool',
        'user_service_access': 'UserServiceAccessTypes',
        'startup_id': 'str'
    }

    attribute_map = {
        'project_id': 'project_id',
        'name': 'name',
        'session_params': 'session_params',
        'command_name': 'command_name',
        'command_params': 'command_params',
        'shell': 'shell',
        'min_workers': 'min_workers',
        'max_workers': 'max_workers',
        'cluster_config': 'cluster_config',
        'build_id': 'build_id',
        'compute_template_id': 'compute_template_id',
        'cloud_id': 'cloud_id',
        'start_session': 'start_session',
        'wait_for_snapshot': 'wait_for_snapshot',
        'idle_timeout': 'idle_timeout',
        'uses_app_config': 'uses_app_config',
        'user_service_access': 'user_service_access',
        'startup_id': 'startup_id'
    }

    def __init__(self, project_id=None, name=None, session_params=None, command_name=None, command_params=None, shell=False, min_workers=None, max_workers=None, cluster_config=None, build_id=None, compute_template_id=None, cloud_id=None, start_session=True, wait_for_snapshot=False, idle_timeout=None, uses_app_config=False, user_service_access=None, startup_id=None, local_vars_configuration=None):  # noqa: E501
        """CreateSessionFromSnapshotOptions - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._project_id = None
        self._name = None
        self._session_params = None
        self._command_name = None
        self._command_params = None
        self._shell = None
        self._min_workers = None
        self._max_workers = None
        self._cluster_config = None
        self._build_id = None
        self._compute_template_id = None
        self._cloud_id = None
        self._start_session = None
        self._wait_for_snapshot = None
        self._idle_timeout = None
        self._uses_app_config = None
        self._user_service_access = None
        self._startup_id = None
        self.discriminator = None

        self.project_id = project_id
        self.name = name
        if session_params is not None:
            self.session_params = session_params
        if command_name is not None:
            self.command_name = command_name
        if command_params is not None:
            self.command_params = command_params
        if shell is not None:
            self.shell = shell
        if min_workers is not None:
            self.min_workers = min_workers
        if max_workers is not None:
            self.max_workers = max_workers
        if cluster_config is not None:
            self.cluster_config = cluster_config
        if build_id is not None:
            self.build_id = build_id
        if compute_template_id is not None:
            self.compute_template_id = compute_template_id
        if cloud_id is not None:
            self.cloud_id = cloud_id
        if start_session is not None:
            self.start_session = start_session
        if wait_for_snapshot is not None:
            self.wait_for_snapshot = wait_for_snapshot
        if idle_timeout is not None:
            self.idle_timeout = idle_timeout
        if uses_app_config is not None:
            self.uses_app_config = uses_app_config
        if user_service_access is not None:
            self.user_service_access = user_service_access
        self.startup_id = startup_id

    @property
    def project_id(self):
        """Gets the project_id of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The project_id of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this CreateSessionFromSnapshotOptions.


        :param project_id: The project_id of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and project_id is None:  # noqa: E501
            raise ValueError("Invalid value for `project_id`, must not be `None`")  # noqa: E501

        self._project_id = project_id

    @property
    def name(self):
        """Gets the name of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The name of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this CreateSessionFromSnapshotOptions.


        :param name: The name of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def session_params(self):
        """Gets the session_params of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The session_params of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: object
        """
        return self._session_params

    @session_params.setter
    def session_params(self, session_params):
        """Sets the session_params of this CreateSessionFromSnapshotOptions.


        :param session_params: The session_params of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: object
        """

        self._session_params = session_params

    @property
    def command_name(self):
        """Gets the command_name of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The command_name of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: str
        """
        return self._command_name

    @command_name.setter
    def command_name(self, command_name):
        """Sets the command_name of this CreateSessionFromSnapshotOptions.


        :param command_name: The command_name of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: str
        """

        self._command_name = command_name

    @property
    def command_params(self):
        """Gets the command_params of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The command_params of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: object
        """
        return self._command_params

    @command_params.setter
    def command_params(self, command_params):
        """Sets the command_params of this CreateSessionFromSnapshotOptions.


        :param command_params: The command_params of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: object
        """

        self._command_params = command_params

    @property
    def shell(self):
        """Gets the shell of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The shell of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: bool
        """
        return self._shell

    @shell.setter
    def shell(self, shell):
        """Sets the shell of this CreateSessionFromSnapshotOptions.


        :param shell: The shell of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: bool
        """

        self._shell = shell

    @property
    def min_workers(self):
        """Gets the min_workers of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The min_workers of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: int
        """
        return self._min_workers

    @min_workers.setter
    def min_workers(self, min_workers):
        """Sets the min_workers of this CreateSessionFromSnapshotOptions.


        :param min_workers: The min_workers of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: int
        """

        self._min_workers = min_workers

    @property
    def max_workers(self):
        """Gets the max_workers of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The max_workers of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: int
        """
        return self._max_workers

    @max_workers.setter
    def max_workers(self, max_workers):
        """Sets the max_workers of this CreateSessionFromSnapshotOptions.


        :param max_workers: The max_workers of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: int
        """

        self._max_workers = max_workers

    @property
    def cluster_config(self):
        """Gets the cluster_config of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The cluster_config of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: WriteClusterConfig
        """
        return self._cluster_config

    @cluster_config.setter
    def cluster_config(self, cluster_config):
        """Sets the cluster_config of this CreateSessionFromSnapshotOptions.


        :param cluster_config: The cluster_config of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: WriteClusterConfig
        """

        self._cluster_config = cluster_config

    @property
    def build_id(self):
        """Gets the build_id of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The build_id of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: str
        """
        return self._build_id

    @build_id.setter
    def build_id(self, build_id):
        """Sets the build_id of this CreateSessionFromSnapshotOptions.


        :param build_id: The build_id of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: str
        """

        self._build_id = build_id

    @property
    def compute_template_id(self):
        """Gets the compute_template_id of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The compute_template_id of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: str
        """
        return self._compute_template_id

    @compute_template_id.setter
    def compute_template_id(self, compute_template_id):
        """Sets the compute_template_id of this CreateSessionFromSnapshotOptions.


        :param compute_template_id: The compute_template_id of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: str
        """

        self._compute_template_id = compute_template_id

    @property
    def cloud_id(self):
        """Gets the cloud_id of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The cloud_id of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: str
        """
        return self._cloud_id

    @cloud_id.setter
    def cloud_id(self, cloud_id):
        """Sets the cloud_id of this CreateSessionFromSnapshotOptions.


        :param cloud_id: The cloud_id of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: str
        """

        self._cloud_id = cloud_id

    @property
    def start_session(self):
        """Gets the start_session of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The start_session of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: bool
        """
        return self._start_session

    @start_session.setter
    def start_session(self, start_session):
        """Sets the start_session of this CreateSessionFromSnapshotOptions.


        :param start_session: The start_session of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: bool
        """

        self._start_session = start_session

    @property
    def wait_for_snapshot(self):
        """Gets the wait_for_snapshot of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The wait_for_snapshot of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: bool
        """
        return self._wait_for_snapshot

    @wait_for_snapshot.setter
    def wait_for_snapshot(self, wait_for_snapshot):
        """Sets the wait_for_snapshot of this CreateSessionFromSnapshotOptions.


        :param wait_for_snapshot: The wait_for_snapshot of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: bool
        """

        self._wait_for_snapshot = wait_for_snapshot

    @property
    def idle_timeout(self):
        """Gets the idle_timeout of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The idle_timeout of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: int
        """
        return self._idle_timeout

    @idle_timeout.setter
    def idle_timeout(self, idle_timeout):
        """Sets the idle_timeout of this CreateSessionFromSnapshotOptions.


        :param idle_timeout: The idle_timeout of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: int
        """

        self._idle_timeout = idle_timeout

    @property
    def uses_app_config(self):
        """Gets the uses_app_config of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The uses_app_config of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: bool
        """
        return self._uses_app_config

    @uses_app_config.setter
    def uses_app_config(self, uses_app_config):
        """Sets the uses_app_config of this CreateSessionFromSnapshotOptions.


        :param uses_app_config: The uses_app_config of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: bool
        """

        self._uses_app_config = uses_app_config

    @property
    def user_service_access(self):
        """Gets the user_service_access of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The user_service_access of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: UserServiceAccessTypes
        """
        return self._user_service_access

    @user_service_access.setter
    def user_service_access(self, user_service_access):
        """Sets the user_service_access of this CreateSessionFromSnapshotOptions.


        :param user_service_access: The user_service_access of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: UserServiceAccessTypes
        """

        self._user_service_access = user_service_access

    @property
    def startup_id(self):
        """Gets the startup_id of this CreateSessionFromSnapshotOptions.  # noqa: E501


        :return: The startup_id of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :rtype: str
        """
        return self._startup_id

    @startup_id.setter
    def startup_id(self, startup_id):
        """Sets the startup_id of this CreateSessionFromSnapshotOptions.


        :param startup_id: The startup_id of this CreateSessionFromSnapshotOptions.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and startup_id is None:  # noqa: E501
            raise ValueError("Invalid value for `startup_id`, must not be `None`")  # noqa: E501

        self._startup_id = startup_id

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
        if not isinstance(other, CreateSessionFromSnapshotOptions):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateSessionFromSnapshotOptions):
            return True

        return self.to_dict() != other.to_dict()
