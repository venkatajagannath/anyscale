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


class Cloud(object):
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
        'provider': 'CloudProviders',
        'region': 'str',
        'credentials': 'str',
        'config': 'CloudConfig',
        'is_k8s': 'bool',
        'is_aioa': 'bool',
        'availability_zones': 'list[str]',
        'is_bring_your_own_resource': 'bool',
        'is_private_cloud': 'bool',
        'cluster_management_stack_version': 'ClusterManagementStackVersions',
        'is_private_service_cloud': 'bool',
        'auto_add_user': 'bool',
        'external_id': 'str',
        'id': 'str',
        'type': 'CloudTypes',
        'creator_id': 'str',
        'created_at': 'datetime',
        'status': 'CloudStatus',
        'state': 'CloudState',
        'version': 'CloudVersion',
        'is_default': 'bool',
        'customer_aggregated_logs_config_id': 'str'
    }

    attribute_map = {
        'name': 'name',
        'provider': 'provider',
        'region': 'region',
        'credentials': 'credentials',
        'config': 'config',
        'is_k8s': 'is_k8s',
        'is_aioa': 'is_aioa',
        'availability_zones': 'availability_zones',
        'is_bring_your_own_resource': 'is_bring_your_own_resource',
        'is_private_cloud': 'is_private_cloud',
        'cluster_management_stack_version': 'cluster_management_stack_version',
        'is_private_service_cloud': 'is_private_service_cloud',
        'auto_add_user': 'auto_add_user',
        'external_id': 'external_id',
        'id': 'id',
        'type': 'type',
        'creator_id': 'creator_id',
        'created_at': 'created_at',
        'status': 'status',
        'state': 'state',
        'version': 'version',
        'is_default': 'is_default',
        'customer_aggregated_logs_config_id': 'customer_aggregated_logs_config_id'
    }

    def __init__(self, name=None, provider=None, region=None, credentials=None, config=None, is_k8s=False, is_aioa=False, availability_zones=None, is_bring_your_own_resource=None, is_private_cloud=False, cluster_management_stack_version=None, is_private_service_cloud=None, auto_add_user=False, external_id=None, id=None, type=None, creator_id=None, created_at=None, status=None, state=None, version=None, is_default=None, customer_aggregated_logs_config_id=None, local_vars_configuration=None):  # noqa: E501
        """Cloud - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self._provider = None
        self._region = None
        self._credentials = None
        self._config = None
        self._is_k8s = None
        self._is_aioa = None
        self._availability_zones = None
        self._is_bring_your_own_resource = None
        self._is_private_cloud = None
        self._cluster_management_stack_version = None
        self._is_private_service_cloud = None
        self._auto_add_user = None
        self._external_id = None
        self._id = None
        self._type = None
        self._creator_id = None
        self._created_at = None
        self._status = None
        self._state = None
        self._version = None
        self._is_default = None
        self._customer_aggregated_logs_config_id = None
        self.discriminator = None

        self.name = name
        self.provider = provider
        self.region = region
        self.credentials = credentials
        if config is not None:
            self.config = config
        if is_k8s is not None:
            self.is_k8s = is_k8s
        if is_aioa is not None:
            self.is_aioa = is_aioa
        if availability_zones is not None:
            self.availability_zones = availability_zones
        if is_bring_your_own_resource is not None:
            self.is_bring_your_own_resource = is_bring_your_own_resource
        if is_private_cloud is not None:
            self.is_private_cloud = is_private_cloud
        if cluster_management_stack_version is not None:
            self.cluster_management_stack_version = cluster_management_stack_version
        if is_private_service_cloud is not None:
            self.is_private_service_cloud = is_private_service_cloud
        if auto_add_user is not None:
            self.auto_add_user = auto_add_user
        if external_id is not None:
            self.external_id = external_id
        self.id = id
        self.type = type
        self.creator_id = creator_id
        self.created_at = created_at
        if status is not None:
            self.status = status
        if state is not None:
            self.state = state
        if version is not None:
            self.version = version
        self.is_default = is_default
        self.customer_aggregated_logs_config_id = customer_aggregated_logs_config_id

    @property
    def name(self):
        """Gets the name of this Cloud.  # noqa: E501

        Name of this Cloud.  # noqa: E501

        :return: The name of this Cloud.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Cloud.

        Name of this Cloud.  # noqa: E501

        :param name: The name of this Cloud.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def provider(self):
        """Gets the provider of this Cloud.  # noqa: E501

        Provider of this Cloud (e.g. AWS).  # noqa: E501

        :return: The provider of this Cloud.  # noqa: E501
        :rtype: CloudProviders
        """
        return self._provider

    @provider.setter
    def provider(self, provider):
        """Sets the provider of this Cloud.

        Provider of this Cloud (e.g. AWS).  # noqa: E501

        :param provider: The provider of this Cloud.  # noqa: E501
        :type: CloudProviders
        """
        if self.local_vars_configuration.client_side_validation and provider is None:  # noqa: E501
            raise ValueError("Invalid value for `provider`, must not be `None`")  # noqa: E501

        self._provider = provider

    @property
    def region(self):
        """Gets the region of this Cloud.  # noqa: E501

        Region this Cloud is operating in. This value needs to be supported by this Cloud's provider. (e.g. us-west-2)  # noqa: E501

        :return: The region of this Cloud.  # noqa: E501
        :rtype: str
        """
        return self._region

    @region.setter
    def region(self, region):
        """Sets the region of this Cloud.

        Region this Cloud is operating in. This value needs to be supported by this Cloud's provider. (e.g. us-west-2)  # noqa: E501

        :param region: The region of this Cloud.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and region is None:  # noqa: E501
            raise ValueError("Invalid value for `region`, must not be `None`")  # noqa: E501

        self._region = region

    @property
    def credentials(self):
        """Gets the credentials of this Cloud.  # noqa: E501

        Credentials needed to interact with this Cloud.  # noqa: E501

        :return: The credentials of this Cloud.  # noqa: E501
        :rtype: str
        """
        return self._credentials

    @credentials.setter
    def credentials(self, credentials):
        """Sets the credentials of this Cloud.

        Credentials needed to interact with this Cloud.  # noqa: E501

        :param credentials: The credentials of this Cloud.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and credentials is None:  # noqa: E501
            raise ValueError("Invalid value for `credentials`, must not be `None`")  # noqa: E501

        self._credentials = credentials

    @property
    def config(self):
        """Gets the config of this Cloud.  # noqa: E501

        Additional configurable properties of this Cloud.  # noqa: E501

        :return: The config of this Cloud.  # noqa: E501
        :rtype: CloudConfig
        """
        return self._config

    @config.setter
    def config(self, config):
        """Sets the config of this Cloud.

        Additional configurable properties of this Cloud.  # noqa: E501

        :param config: The config of this Cloud.  # noqa: E501
        :type: CloudConfig
        """

        self._config = config

    @property
    def is_k8s(self):
        """Gets the is_k8s of this Cloud.  # noqa: E501

        Whether this cloud is managed via Kubernetes.  # noqa: E501

        :return: The is_k8s of this Cloud.  # noqa: E501
        :rtype: bool
        """
        return self._is_k8s

    @is_k8s.setter
    def is_k8s(self, is_k8s):
        """Sets the is_k8s of this Cloud.

        Whether this cloud is managed via Kubernetes.  # noqa: E501

        :param is_k8s: The is_k8s of this Cloud.  # noqa: E501
        :type: bool
        """

        self._is_k8s = is_k8s

    @property
    def is_aioa(self):
        """Gets the is_aioa of this Cloud.  # noqa: E501

        Whether this cloud is an AIOA cloud.  # noqa: E501

        :return: The is_aioa of this Cloud.  # noqa: E501
        :rtype: bool
        """
        return self._is_aioa

    @is_aioa.setter
    def is_aioa(self, is_aioa):
        """Sets the is_aioa of this Cloud.

        Whether this cloud is an AIOA cloud.  # noqa: E501

        :param is_aioa: The is_aioa of this Cloud.  # noqa: E501
        :type: bool
        """

        self._is_aioa = is_aioa

    @property
    def availability_zones(self):
        """Gets the availability_zones of this Cloud.  # noqa: E501

        The availability zones that instances of this cloud are allowed to be launched in.  # noqa: E501

        :return: The availability_zones of this Cloud.  # noqa: E501
        :rtype: list[str]
        """
        return self._availability_zones

    @availability_zones.setter
    def availability_zones(self, availability_zones):
        """Sets the availability_zones of this Cloud.

        The availability zones that instances of this cloud are allowed to be launched in.  # noqa: E501

        :param availability_zones: The availability_zones of this Cloud.  # noqa: E501
        :type: list[str]
        """

        self._availability_zones = availability_zones

    @property
    def is_bring_your_own_resource(self):
        """Gets the is_bring_your_own_resource of this Cloud.  # noqa: E501

        Whether the resources of this cloud are provided by the customer.  # noqa: E501

        :return: The is_bring_your_own_resource of this Cloud.  # noqa: E501
        :rtype: bool
        """
        return self._is_bring_your_own_resource

    @is_bring_your_own_resource.setter
    def is_bring_your_own_resource(self, is_bring_your_own_resource):
        """Sets the is_bring_your_own_resource of this Cloud.

        Whether the resources of this cloud are provided by the customer.  # noqa: E501

        :param is_bring_your_own_resource: The is_bring_your_own_resource of this Cloud.  # noqa: E501
        :type: bool
        """

        self._is_bring_your_own_resource = is_bring_your_own_resource

    @property
    def is_private_cloud(self):
        """Gets the is_private_cloud of this Cloud.  # noqa: E501

        Whether this cloud is a private cloud.  # noqa: E501

        :return: The is_private_cloud of this Cloud.  # noqa: E501
        :rtype: bool
        """
        return self._is_private_cloud

    @is_private_cloud.setter
    def is_private_cloud(self, is_private_cloud):
        """Sets the is_private_cloud of this Cloud.

        Whether this cloud is a private cloud.  # noqa: E501

        :param is_private_cloud: The is_private_cloud of this Cloud.  # noqa: E501
        :type: bool
        """

        self._is_private_cloud = is_private_cloud

    @property
    def cluster_management_stack_version(self):
        """Gets the cluster_management_stack_version of this Cloud.  # noqa: E501

        The cluster management stack version of the cloud.  # noqa: E501

        :return: The cluster_management_stack_version of this Cloud.  # noqa: E501
        :rtype: ClusterManagementStackVersions
        """
        return self._cluster_management_stack_version

    @cluster_management_stack_version.setter
    def cluster_management_stack_version(self, cluster_management_stack_version):
        """Sets the cluster_management_stack_version of this Cloud.

        The cluster management stack version of the cloud.  # noqa: E501

        :param cluster_management_stack_version: The cluster_management_stack_version of this Cloud.  # noqa: E501
        :type: ClusterManagementStackVersions
        """

        self._cluster_management_stack_version = cluster_management_stack_version

    @property
    def is_private_service_cloud(self):
        """Gets the is_private_service_cloud of this Cloud.  # noqa: E501

        Whether services created in this cloud should be private.  # noqa: E501

        :return: The is_private_service_cloud of this Cloud.  # noqa: E501
        :rtype: bool
        """
        return self._is_private_service_cloud

    @is_private_service_cloud.setter
    def is_private_service_cloud(self, is_private_service_cloud):
        """Sets the is_private_service_cloud of this Cloud.

        Whether services created in this cloud should be private.  # noqa: E501

        :param is_private_service_cloud: The is_private_service_cloud of this Cloud.  # noqa: E501
        :type: bool
        """

        self._is_private_service_cloud = is_private_service_cloud

    @property
    def auto_add_user(self):
        """Gets the auto_add_user of this Cloud.  # noqa: E501

        Whether all users in the organization should be automatically added to this cloud. This field is only relevant for organizations with cloud isolation enabled, because all users in the organization automatically have access to all clouds if cloud isolation is not enabled.  # noqa: E501

        :return: The auto_add_user of this Cloud.  # noqa: E501
        :rtype: bool
        """
        return self._auto_add_user

    @auto_add_user.setter
    def auto_add_user(self, auto_add_user):
        """Sets the auto_add_user of this Cloud.

        Whether all users in the organization should be automatically added to this cloud. This field is only relevant for organizations with cloud isolation enabled, because all users in the organization automatically have access to all clouds if cloud isolation is not enabled.  # noqa: E501

        :param auto_add_user: The auto_add_user of this Cloud.  # noqa: E501
        :type: bool
        """

        self._auto_add_user = auto_add_user

    @property
    def external_id(self):
        """Gets the external_id of this Cloud.  # noqa: E501

        The trust policy external ID specified by the user for the cloud control plane role. It must start with the organization ID.  # noqa: E501

        :return: The external_id of this Cloud.  # noqa: E501
        :rtype: str
        """
        return self._external_id

    @external_id.setter
    def external_id(self, external_id):
        """Sets the external_id of this Cloud.

        The trust policy external ID specified by the user for the cloud control plane role. It must start with the organization ID.  # noqa: E501

        :param external_id: The external_id of this Cloud.  # noqa: E501
        :type: str
        """

        self._external_id = external_id

    @property
    def id(self):
        """Gets the id of this Cloud.  # noqa: E501

        Server assigned unique identifier.  # noqa: E501

        :return: The id of this Cloud.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Cloud.

        Server assigned unique identifier.  # noqa: E501

        :param id: The id of this Cloud.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def type(self):
        """Gets the type of this Cloud.  # noqa: E501


        :return: The type of this Cloud.  # noqa: E501
        :rtype: CloudTypes
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Cloud.


        :param type: The type of this Cloud.  # noqa: E501
        :type: CloudTypes
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501

        self._type = type

    @property
    def creator_id(self):
        """Gets the creator_id of this Cloud.  # noqa: E501

        ID of the User who created this Cloud.  # noqa: E501

        :return: The creator_id of this Cloud.  # noqa: E501
        :rtype: str
        """
        return self._creator_id

    @creator_id.setter
    def creator_id(self, creator_id):
        """Sets the creator_id of this Cloud.

        ID of the User who created this Cloud.  # noqa: E501

        :param creator_id: The creator_id of this Cloud.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and creator_id is None:  # noqa: E501
            raise ValueError("Invalid value for `creator_id`, must not be `None`")  # noqa: E501

        self._creator_id = creator_id

    @property
    def created_at(self):
        """Gets the created_at of this Cloud.  # noqa: E501

        Time when this Cloud was created.  # noqa: E501

        :return: The created_at of this Cloud.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this Cloud.

        Time when this Cloud was created.  # noqa: E501

        :param created_at: The created_at of this Cloud.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and created_at is None:  # noqa: E501
            raise ValueError("Invalid value for `created_at`, must not be `None`")  # noqa: E501

        self._created_at = created_at

    @property
    def status(self):
        """Gets the status of this Cloud.  # noqa: E501

        The status of this cloud.  # noqa: E501

        :return: The status of this Cloud.  # noqa: E501
        :rtype: CloudStatus
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this Cloud.

        The status of this cloud.  # noqa: E501

        :param status: The status of this Cloud.  # noqa: E501
        :type: CloudStatus
        """

        self._status = status

    @property
    def state(self):
        """Gets the state of this Cloud.  # noqa: E501

        The state of this cloud.  # noqa: E501

        :return: The state of this Cloud.  # noqa: E501
        :rtype: CloudState
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this Cloud.

        The state of this cloud.  # noqa: E501

        :param state: The state of this Cloud.  # noqa: E501
        :type: CloudState
        """

        self._state = state

    @property
    def version(self):
        """Gets the version of this Cloud.  # noqa: E501

        The version of the cloud.  # noqa: E501

        :return: The version of this Cloud.  # noqa: E501
        :rtype: CloudVersion
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this Cloud.

        The version of the cloud.  # noqa: E501

        :param version: The version of this Cloud.  # noqa: E501
        :type: CloudVersion
        """

        self._version = version

    @property
    def is_default(self):
        """Gets the is_default of this Cloud.  # noqa: E501

        Whether this cloud is the default cloud.  # noqa: E501

        :return: The is_default of this Cloud.  # noqa: E501
        :rtype: bool
        """
        return self._is_default

    @is_default.setter
    def is_default(self, is_default):
        """Sets the is_default of this Cloud.

        Whether this cloud is the default cloud.  # noqa: E501

        :param is_default: The is_default of this Cloud.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and is_default is None:  # noqa: E501
            raise ValueError("Invalid value for `is_default`, must not be `None`")  # noqa: E501

        self._is_default = is_default

    @property
    def customer_aggregated_logs_config_id(self):
        """Gets the customer_aggregated_logs_config_id of this Cloud.  # noqa: E501

        the id of the customer aggregated logs config associated with this cloud.  # noqa: E501

        :return: The customer_aggregated_logs_config_id of this Cloud.  # noqa: E501
        :rtype: str
        """
        return self._customer_aggregated_logs_config_id

    @customer_aggregated_logs_config_id.setter
    def customer_aggregated_logs_config_id(self, customer_aggregated_logs_config_id):
        """Sets the customer_aggregated_logs_config_id of this Cloud.

        the id of the customer aggregated logs config associated with this cloud.  # noqa: E501

        :param customer_aggregated_logs_config_id: The customer_aggregated_logs_config_id of this Cloud.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and customer_aggregated_logs_config_id is None:  # noqa: E501
            raise ValueError("Invalid value for `customer_aggregated_logs_config_id`, must not be `None`")  # noqa: E501

        self._customer_aggregated_logs_config_id = customer_aggregated_logs_config_id

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
        if not isinstance(other, Cloud):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Cloud):
            return True

        return self.to_dict() != other.to_dict()
