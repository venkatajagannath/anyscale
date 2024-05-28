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


class DecoratedProductionServiceV2VersionAPIModel(object):
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
        'id': 'str',
        'created_at': 'datetime',
        'weight': 'int',
        'current_weight': 'int',
        'version': 'str',
        'ray_serve_config': 'object',
        'ray_gcs_external_storage_config': 'RayGCSExternalStorageConfig',
        'build_id': 'str',
        'compute_config_id': 'str',
        'production_job_ids': 'list[str]',
        'current_state': 'ServiceVersionState'
    }

    attribute_map = {
        'id': 'id',
        'created_at': 'created_at',
        'weight': 'weight',
        'current_weight': 'current_weight',
        'version': 'version',
        'ray_serve_config': 'ray_serve_config',
        'ray_gcs_external_storage_config': 'ray_gcs_external_storage_config',
        'build_id': 'build_id',
        'compute_config_id': 'compute_config_id',
        'production_job_ids': 'production_job_ids',
        'current_state': 'current_state'
    }

    def __init__(self, id=None, created_at=None, weight=None, current_weight=None, version=None, ray_serve_config=None, ray_gcs_external_storage_config=None, build_id=None, compute_config_id=None, production_job_ids=None, current_state=None, local_vars_configuration=None):  # noqa: E501
        """DecoratedProductionServiceV2VersionAPIModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._created_at = None
        self._weight = None
        self._current_weight = None
        self._version = None
        self._ray_serve_config = None
        self._ray_gcs_external_storage_config = None
        self._build_id = None
        self._compute_config_id = None
        self._production_job_ids = None
        self._current_state = None
        self.discriminator = None

        self.id = id
        self.created_at = created_at
        self.weight = weight
        if current_weight is not None:
            self.current_weight = current_weight
        self.version = version
        self.ray_serve_config = ray_serve_config
        if ray_gcs_external_storage_config is not None:
            self.ray_gcs_external_storage_config = ray_gcs_external_storage_config
        self.build_id = build_id
        self.compute_config_id = compute_config_id
        self.production_job_ids = production_job_ids
        self.current_state = current_state

    @property
    def id(self):
        """Gets the id of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501

        Id of the Service Version  # noqa: E501

        :return: The id of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this DecoratedProductionServiceV2VersionAPIModel.

        Id of the Service Version  # noqa: E501

        :param id: The id of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def created_at(self):
        """Gets the created_at of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501

        Time the version was created  # noqa: E501

        :return: The created_at of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this DecoratedProductionServiceV2VersionAPIModel.

        Time the version was created  # noqa: E501

        :param created_at: The created_at of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and created_at is None:  # noqa: E501
            raise ValueError("Invalid value for `created_at`, must not be `None`")  # noqa: E501

        self._created_at = created_at

    @property
    def weight(self):
        """Gets the weight of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501

        The target percentage of traffic sent to this version. This is a number between 0 and 100.  # noqa: E501

        :return: The weight of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :rtype: int
        """
        return self._weight

    @weight.setter
    def weight(self, weight):
        """Sets the weight of this DecoratedProductionServiceV2VersionAPIModel.

        The target percentage of traffic sent to this version. This is a number between 0 and 100.  # noqa: E501

        :param weight: The weight of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and weight is None:  # noqa: E501
            raise ValueError("Invalid value for `weight`, must not be `None`")  # noqa: E501

        self._weight = weight

    @property
    def current_weight(self):
        """Gets the current_weight of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501

        The current percentage of traffic sent to this version. This is a number between 0 and 100.  # noqa: E501

        :return: The current_weight of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :rtype: int
        """
        return self._current_weight

    @current_weight.setter
    def current_weight(self, current_weight):
        """Sets the current_weight of this DecoratedProductionServiceV2VersionAPIModel.

        The current percentage of traffic sent to this version. This is a number between 0 and 100.  # noqa: E501

        :param current_weight: The current_weight of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :type: int
        """

        self._current_weight = current_weight

    @property
    def version(self):
        """Gets the version of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501

        The version string identifier for this version  # noqa: E501

        :return: The version of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this DecoratedProductionServiceV2VersionAPIModel.

        The version string identifier for this version  # noqa: E501

        :param version: The version of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and version is None:  # noqa: E501
            raise ValueError("Invalid value for `version`, must not be `None`")  # noqa: E501

        self._version = version

    @property
    def ray_serve_config(self):
        """Gets the ray_serve_config of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501


        :return: The ray_serve_config of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :rtype: object
        """
        return self._ray_serve_config

    @ray_serve_config.setter
    def ray_serve_config(self, ray_serve_config):
        """Sets the ray_serve_config of this DecoratedProductionServiceV2VersionAPIModel.


        :param ray_serve_config: The ray_serve_config of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :type: object
        """
        if self.local_vars_configuration.client_side_validation and ray_serve_config is None:  # noqa: E501
            raise ValueError("Invalid value for `ray_serve_config`, must not be `None`")  # noqa: E501

        self._ray_serve_config = ray_serve_config

    @property
    def ray_gcs_external_storage_config(self):
        """Gets the ray_gcs_external_storage_config of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501

        Config for the Ray GCS to connect to external storage. If populated, head node fault tolerance is enabled for this service.  # noqa: E501

        :return: The ray_gcs_external_storage_config of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :rtype: RayGCSExternalStorageConfig
        """
        return self._ray_gcs_external_storage_config

    @ray_gcs_external_storage_config.setter
    def ray_gcs_external_storage_config(self, ray_gcs_external_storage_config):
        """Sets the ray_gcs_external_storage_config of this DecoratedProductionServiceV2VersionAPIModel.

        Config for the Ray GCS to connect to external storage. If populated, head node fault tolerance is enabled for this service.  # noqa: E501

        :param ray_gcs_external_storage_config: The ray_gcs_external_storage_config of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :type: RayGCSExternalStorageConfig
        """

        self._ray_gcs_external_storage_config = ray_gcs_external_storage_config

    @property
    def build_id(self):
        """Gets the build_id of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501

        The id of the cluster env build. This id will determine the docker image your Service is run using.  # noqa: E501

        :return: The build_id of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :rtype: str
        """
        return self._build_id

    @build_id.setter
    def build_id(self, build_id):
        """Sets the build_id of this DecoratedProductionServiceV2VersionAPIModel.

        The id of the cluster env build. This id will determine the docker image your Service is run using.  # noqa: E501

        :param build_id: The build_id of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and build_id is None:  # noqa: E501
            raise ValueError("Invalid value for `build_id`, must not be `None`")  # noqa: E501

        self._build_id = build_id

    @property
    def compute_config_id(self):
        """Gets the compute_config_id of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501

        The id of the compute configuration that you want to use. This id will specify the resources required for your Service.The compute template includes a `cloud_id` that cannot be updated.  # noqa: E501

        :return: The compute_config_id of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :rtype: str
        """
        return self._compute_config_id

    @compute_config_id.setter
    def compute_config_id(self, compute_config_id):
        """Sets the compute_config_id of this DecoratedProductionServiceV2VersionAPIModel.

        The id of the compute configuration that you want to use. This id will specify the resources required for your Service.The compute template includes a `cloud_id` that cannot be updated.  # noqa: E501

        :param compute_config_id: The compute_config_id of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and compute_config_id is None:  # noqa: E501
            raise ValueError("Invalid value for `compute_config_id`, must not be `None`")  # noqa: E501

        self._compute_config_id = compute_config_id

    @property
    def production_job_ids(self):
        """Gets the production_job_ids of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501

        The list of production job ids associated with this service version.  # noqa: E501

        :return: The production_job_ids of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :rtype: list[str]
        """
        return self._production_job_ids

    @production_job_ids.setter
    def production_job_ids(self, production_job_ids):
        """Sets the production_job_ids of this DecoratedProductionServiceV2VersionAPIModel.

        The list of production job ids associated with this service version.  # noqa: E501

        :param production_job_ids: The production_job_ids of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :type: list[str]
        """
        if self.local_vars_configuration.client_side_validation and production_job_ids is None:  # noqa: E501
            raise ValueError("Invalid value for `production_job_ids`, must not be `None`")  # noqa: E501

        self._production_job_ids = production_job_ids

    @property
    def current_state(self):
        """Gets the current_state of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501

        The current state of the service version.  # noqa: E501

        :return: The current_state of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :rtype: ServiceVersionState
        """
        return self._current_state

    @current_state.setter
    def current_state(self, current_state):
        """Sets the current_state of this DecoratedProductionServiceV2VersionAPIModel.

        The current state of the service version.  # noqa: E501

        :param current_state: The current_state of this DecoratedProductionServiceV2VersionAPIModel.  # noqa: E501
        :type: ServiceVersionState
        """
        if self.local_vars_configuration.client_side_validation and current_state is None:  # noqa: E501
            raise ValueError("Invalid value for `current_state`, must not be `None`")  # noqa: E501

        self._current_state = current_state

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
        if not isinstance(other, DecoratedProductionServiceV2VersionAPIModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DecoratedProductionServiceV2VersionAPIModel):
            return True

        return self.to_dict() != other.to_dict()
