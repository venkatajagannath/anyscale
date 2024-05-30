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


class UpdateComputeTemplateConfig(object):
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
        'cloud_id': 'str',
        'max_workers': 'int',
        'region': 'str',
        'allowed_azs': 'list[str]',
        'head_node_type': 'ComputeNodeType',
        'worker_node_types': 'list[WorkerNodeType]',
        'aws_advanced_configurations_json': 'object',
        'aws': 'AWSNodeOptions',
        'gcp_advanced_configurations_json': 'object',
        'gcp': 'GCPNodeOptions',
        'azure': 'object',
        'maximum_uptime_minutes': 'int',
        'auto_select_worker_config': 'bool',
        'flags': 'object',
        'idle_termination_minutes': 'int'
    }

    attribute_map = {
        'cloud_id': 'cloud_id',
        'max_workers': 'max_workers',
        'region': 'region',
        'allowed_azs': 'allowed_azs',
        'head_node_type': 'head_node_type',
        'worker_node_types': 'worker_node_types',
        'aws_advanced_configurations_json': 'aws_advanced_configurations_json',
        'aws': 'aws',
        'gcp_advanced_configurations_json': 'gcp_advanced_configurations_json',
        'gcp': 'gcp',
        'azure': 'azure',
        'maximum_uptime_minutes': 'maximum_uptime_minutes',
        'auto_select_worker_config': 'auto_select_worker_config',
        'flags': 'flags',
        'idle_termination_minutes': 'idle_termination_minutes'
    }

    def __init__(self, cloud_id=None, max_workers=None, region=None, allowed_azs=None, head_node_type=None, worker_node_types=None, aws_advanced_configurations_json=None, aws=None, gcp_advanced_configurations_json=None, gcp=None, azure=None, maximum_uptime_minutes=None, auto_select_worker_config=False, flags=None, idle_termination_minutes=120, local_vars_configuration=None):  # noqa: E501
        """UpdateComputeTemplateConfig - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._cloud_id = None
        self._max_workers = None
        self._region = None
        self._allowed_azs = None
        self._head_node_type = None
        self._worker_node_types = None
        self._aws_advanced_configurations_json = None
        self._aws = None
        self._gcp_advanced_configurations_json = None
        self._gcp = None
        self._azure = None
        self._maximum_uptime_minutes = None
        self._auto_select_worker_config = None
        self._flags = None
        self._idle_termination_minutes = None
        self.discriminator = None

        self.cloud_id = cloud_id
        if max_workers is not None:
            self.max_workers = max_workers
        self.region = region
        if allowed_azs is not None:
            self.allowed_azs = allowed_azs
        self.head_node_type = head_node_type
        if worker_node_types is not None:
            self.worker_node_types = worker_node_types
        if aws_advanced_configurations_json is not None:
            self.aws_advanced_configurations_json = aws_advanced_configurations_json
        if aws is not None:
            self.aws = aws
        if gcp_advanced_configurations_json is not None:
            self.gcp_advanced_configurations_json = gcp_advanced_configurations_json
        if gcp is not None:
            self.gcp = gcp
        if azure is not None:
            self.azure = azure
        if maximum_uptime_minutes is not None:
            self.maximum_uptime_minutes = maximum_uptime_minutes
        if auto_select_worker_config is not None:
            self.auto_select_worker_config = auto_select_worker_config
        if flags is not None:
            self.flags = flags
        if idle_termination_minutes is not None:
            self.idle_termination_minutes = idle_termination_minutes

    @property
    def cloud_id(self):
        """Gets the cloud_id of this UpdateComputeTemplateConfig.  # noqa: E501

        The ID of the Anyscale cloud to use for launching sessions.  # noqa: E501

        :return: The cloud_id of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: str
        """
        return self._cloud_id

    @cloud_id.setter
    def cloud_id(self, cloud_id):
        """Sets the cloud_id of this UpdateComputeTemplateConfig.

        The ID of the Anyscale cloud to use for launching sessions.  # noqa: E501

        :param cloud_id: The cloud_id of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and cloud_id is None:  # noqa: E501
            raise ValueError("Invalid value for `cloud_id`, must not be `None`")  # noqa: E501

        self._cloud_id = cloud_id

    @property
    def max_workers(self):
        """Gets the max_workers of this UpdateComputeTemplateConfig.  # noqa: E501

        Desired limit on total running workers for this session.  # noqa: E501

        :return: The max_workers of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: int
        """
        return self._max_workers

    @max_workers.setter
    def max_workers(self, max_workers):
        """Sets the max_workers of this UpdateComputeTemplateConfig.

        Desired limit on total running workers for this session.  # noqa: E501

        :param max_workers: The max_workers of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: int
        """

        self._max_workers = max_workers

    @property
    def region(self):
        """Gets the region of this UpdateComputeTemplateConfig.  # noqa: E501

        The region to launch sessions in, e.g. \"us-west-2\".  # noqa: E501

        :return: The region of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: str
        """
        return self._region

    @region.setter
    def region(self, region):
        """Sets the region of this UpdateComputeTemplateConfig.

        The region to launch sessions in, e.g. \"us-west-2\".  # noqa: E501

        :param region: The region of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and region is None:  # noqa: E501
            raise ValueError("Invalid value for `region`, must not be `None`")  # noqa: E501

        self._region = region

    @property
    def allowed_azs(self):
        """Gets the allowed_azs of this UpdateComputeTemplateConfig.  # noqa: E501

        The availability zones that sessions are allowed to be launched in, e.g. \"us-west-2a\". If not specified or \"any\" is provided as the option, any AZ may be used. If \"any\" is provided, it must be the only item in the list.  # noqa: E501

        :return: The allowed_azs of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: list[str]
        """
        return self._allowed_azs

    @allowed_azs.setter
    def allowed_azs(self, allowed_azs):
        """Sets the allowed_azs of this UpdateComputeTemplateConfig.

        The availability zones that sessions are allowed to be launched in, e.g. \"us-west-2a\". If not specified or \"any\" is provided as the option, any AZ may be used. If \"any\" is provided, it must be the only item in the list.  # noqa: E501

        :param allowed_azs: The allowed_azs of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: list[str]
        """

        self._allowed_azs = allowed_azs

    @property
    def head_node_type(self):
        """Gets the head_node_type of this UpdateComputeTemplateConfig.  # noqa: E501

        Node configuration to use for the head node.   # noqa: E501

        :return: The head_node_type of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: ComputeNodeType
        """
        return self._head_node_type

    @head_node_type.setter
    def head_node_type(self, head_node_type):
        """Sets the head_node_type of this UpdateComputeTemplateConfig.

        Node configuration to use for the head node.   # noqa: E501

        :param head_node_type: The head_node_type of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: ComputeNodeType
        """
        if self.local_vars_configuration.client_side_validation and head_node_type is None:  # noqa: E501
            raise ValueError("Invalid value for `head_node_type`, must not be `None`")  # noqa: E501

        self._head_node_type = head_node_type

    @property
    def worker_node_types(self):
        """Gets the worker_node_types of this UpdateComputeTemplateConfig.  # noqa: E501

        A list of node types to use for worker nodes.   # noqa: E501

        :return: The worker_node_types of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: list[WorkerNodeType]
        """
        return self._worker_node_types

    @worker_node_types.setter
    def worker_node_types(self, worker_node_types):
        """Sets the worker_node_types of this UpdateComputeTemplateConfig.

        A list of node types to use for worker nodes.   # noqa: E501

        :param worker_node_types: The worker_node_types of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: list[WorkerNodeType]
        """

        self._worker_node_types = worker_node_types

    @property
    def aws_advanced_configurations_json(self):
        """Gets the aws_advanced_configurations_json of this UpdateComputeTemplateConfig.  # noqa: E501

        The advanced configuration json that we pass directly AWS APIs when launching an instance. We may do some validation on this json and reject the json if it is using a configuration that Anyscale does not support.  # noqa: E501

        :return: The aws_advanced_configurations_json of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: object
        """
        return self._aws_advanced_configurations_json

    @aws_advanced_configurations_json.setter
    def aws_advanced_configurations_json(self, aws_advanced_configurations_json):
        """Sets the aws_advanced_configurations_json of this UpdateComputeTemplateConfig.

        The advanced configuration json that we pass directly AWS APIs when launching an instance. We may do some validation on this json and reject the json if it is using a configuration that Anyscale does not support.  # noqa: E501

        :param aws_advanced_configurations_json: The aws_advanced_configurations_json of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: object
        """

        self._aws_advanced_configurations_json = aws_advanced_configurations_json

    @property
    def aws(self):
        """Gets the aws of this UpdateComputeTemplateConfig.  # noqa: E501

        DEPRECATED: Please provide instance configuration in the `aws_advanced_configurations_json` field. Fields specific to AWS node types.  # noqa: E501

        :return: The aws of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: AWSNodeOptions
        """
        return self._aws

    @aws.setter
    def aws(self, aws):
        """Sets the aws of this UpdateComputeTemplateConfig.

        DEPRECATED: Please provide instance configuration in the `aws_advanced_configurations_json` field. Fields specific to AWS node types.  # noqa: E501

        :param aws: The aws of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: AWSNodeOptions
        """

        self._aws = aws

    @property
    def gcp_advanced_configurations_json(self):
        """Gets the gcp_advanced_configurations_json of this UpdateComputeTemplateConfig.  # noqa: E501

        The advanced configuration json that we pass directly GCP APIs when launching an instance. We may do some validation on this json and reject the json if it is using a configuration that Anyscale does not support.  # noqa: E501

        :return: The gcp_advanced_configurations_json of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: object
        """
        return self._gcp_advanced_configurations_json

    @gcp_advanced_configurations_json.setter
    def gcp_advanced_configurations_json(self, gcp_advanced_configurations_json):
        """Sets the gcp_advanced_configurations_json of this UpdateComputeTemplateConfig.

        The advanced configuration json that we pass directly GCP APIs when launching an instance. We may do some validation on this json and reject the json if it is using a configuration that Anyscale does not support.  # noqa: E501

        :param gcp_advanced_configurations_json: The gcp_advanced_configurations_json of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: object
        """

        self._gcp_advanced_configurations_json = gcp_advanced_configurations_json

    @property
    def gcp(self):
        """Gets the gcp of this UpdateComputeTemplateConfig.  # noqa: E501

        DEPRECATED: Please provide instance configuration in the `gcp_advanced_configurations_json` field. Fields specific to GCP node types.  # noqa: E501

        :return: The gcp of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: GCPNodeOptions
        """
        return self._gcp

    @gcp.setter
    def gcp(self, gcp):
        """Sets the gcp of this UpdateComputeTemplateConfig.

        DEPRECATED: Please provide instance configuration in the `gcp_advanced_configurations_json` field. Fields specific to GCP node types.  # noqa: E501

        :param gcp: The gcp of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: GCPNodeOptions
        """

        self._gcp = gcp

    @property
    def azure(self):
        """Gets the azure of this UpdateComputeTemplateConfig.  # noqa: E501

        DEPRECATED: We don't currently support azure. Fields specific to Azure node types.  # noqa: E501

        :return: The azure of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: object
        """
        return self._azure

    @azure.setter
    def azure(self, azure):
        """Sets the azure of this UpdateComputeTemplateConfig.

        DEPRECATED: We don't currently support azure. Fields specific to Azure node types.  # noqa: E501

        :param azure: The azure of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: object
        """

        self._azure = azure

    @property
    def maximum_uptime_minutes(self):
        """Gets the maximum_uptime_minutes of this UpdateComputeTemplateConfig.  # noqa: E501

        If set to a positive number, Anyscale will terminate the cluster this many minutes after cluster start.  # noqa: E501

        :return: The maximum_uptime_minutes of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: int
        """
        return self._maximum_uptime_minutes

    @maximum_uptime_minutes.setter
    def maximum_uptime_minutes(self, maximum_uptime_minutes):
        """Sets the maximum_uptime_minutes of this UpdateComputeTemplateConfig.

        If set to a positive number, Anyscale will terminate the cluster this many minutes after cluster start.  # noqa: E501

        :param maximum_uptime_minutes: The maximum_uptime_minutes of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: int
        """

        self._maximum_uptime_minutes = maximum_uptime_minutes

    @property
    def auto_select_worker_config(self):
        """Gets the auto_select_worker_config of this UpdateComputeTemplateConfig.  # noqa: E501

        If set to true, worker node groups will automatically be selected based on workload.  # noqa: E501

        :return: The auto_select_worker_config of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: bool
        """
        return self._auto_select_worker_config

    @auto_select_worker_config.setter
    def auto_select_worker_config(self, auto_select_worker_config):
        """Sets the auto_select_worker_config of this UpdateComputeTemplateConfig.

        If set to true, worker node groups will automatically be selected based on workload.  # noqa: E501

        :param auto_select_worker_config: The auto_select_worker_config of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: bool
        """

        self._auto_select_worker_config = auto_select_worker_config

    @property
    def flags(self):
        """Gets the flags of this UpdateComputeTemplateConfig.  # noqa: E501

        A set of advanced cluster-level flags that can be used to configure a particular workload.  # noqa: E501

        :return: The flags of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: object
        """
        return self._flags

    @flags.setter
    def flags(self, flags):
        """Sets the flags of this UpdateComputeTemplateConfig.

        A set of advanced cluster-level flags that can be used to configure a particular workload.  # noqa: E501

        :param flags: The flags of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: object
        """

        self._flags = flags

    @property
    def idle_termination_minutes(self):
        """Gets the idle_termination_minutes of this UpdateComputeTemplateConfig.  # noqa: E501

        If set to a positive number, Anyscale will terminate the cluster this many minutes after the cluster is idle. Idle time is defined as the time during which a Cluster is not running a user command or a Ray driver. Time spent running commands on Jupyter or ssh is still considered 'idle'. To disable, set this field to 0.  # noqa: E501

        :return: The idle_termination_minutes of this UpdateComputeTemplateConfig.  # noqa: E501
        :rtype: int
        """
        return self._idle_termination_minutes

    @idle_termination_minutes.setter
    def idle_termination_minutes(self, idle_termination_minutes):
        """Sets the idle_termination_minutes of this UpdateComputeTemplateConfig.

        If set to a positive number, Anyscale will terminate the cluster this many minutes after the cluster is idle. Idle time is defined as the time during which a Cluster is not running a user command or a Ray driver. Time spent running commands on Jupyter or ssh is still considered 'idle'. To disable, set this field to 0.  # noqa: E501

        :param idle_termination_minutes: The idle_termination_minutes of this UpdateComputeTemplateConfig.  # noqa: E501
        :type: int
        """
        if (self.local_vars_configuration.client_side_validation and
                idle_termination_minutes is not None and idle_termination_minutes < 0):  # noqa: E501
            raise ValueError("Invalid value for `idle_termination_minutes`, must be a value greater than or equal to `0`")  # noqa: E501

        self._idle_termination_minutes = idle_termination_minutes

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
        if not isinstance(other, UpdateComputeTemplateConfig):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UpdateComputeTemplateConfig):
            return True

        return self.to_dict() != other.to_dict()
