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


class ProductionJobConfig(object):
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
        'entrypoint': 'str',
        'ray_serve_config': 'object',
        'runtime_env': 'RayRuntimeEnvConfig',
        'build_id': 'str',
        'compute_config_id': 'str',
        'compute_config': 'CreateClusterComputeConfig',
        'max_retries': 'int',
        'runtime_env_config': 'RayRuntimeEnvConfig'
    }

    attribute_map = {
        'entrypoint': 'entrypoint',
        'ray_serve_config': 'ray_serve_config',
        'runtime_env': 'runtime_env',
        'build_id': 'build_id',
        'compute_config_id': 'compute_config_id',
        'compute_config': 'compute_config',
        'max_retries': 'max_retries',
        'runtime_env_config': 'runtime_env_config'
    }

    def __init__(self, entrypoint='', ray_serve_config=None, runtime_env=None, build_id=None, compute_config_id=None, compute_config=None, max_retries=5, runtime_env_config=None, local_vars_configuration=None):  # noqa: E501
        """ProductionJobConfig - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._entrypoint = None
        self._ray_serve_config = None
        self._runtime_env = None
        self._build_id = None
        self._compute_config_id = None
        self._compute_config = None
        self._max_retries = None
        self._runtime_env_config = None
        self.discriminator = None

        if entrypoint is not None:
            self.entrypoint = entrypoint
        if ray_serve_config is not None:
            self.ray_serve_config = ray_serve_config
        if runtime_env is not None:
            self.runtime_env = runtime_env
        self.build_id = build_id
        self.compute_config_id = compute_config_id
        if compute_config is not None:
            self.compute_config = compute_config
        if max_retries is not None:
            self.max_retries = max_retries
        if runtime_env_config is not None:
            self.runtime_env_config = runtime_env_config

    @property
    def entrypoint(self):
        """Gets the entrypoint of this ProductionJobConfig.  # noqa: E501

        A script that will be run to start your job.This command will be run in the root directory of the specified runtime env. Eg. 'python script.py'  # noqa: E501

        :return: The entrypoint of this ProductionJobConfig.  # noqa: E501
        :rtype: str
        """
        return self._entrypoint

    @entrypoint.setter
    def entrypoint(self, entrypoint):
        """Sets the entrypoint of this ProductionJobConfig.

        A script that will be run to start your job.This command will be run in the root directory of the specified runtime env. Eg. 'python script.py'  # noqa: E501

        :param entrypoint: The entrypoint of this ProductionJobConfig.  # noqa: E501
        :type: str
        """

        self._entrypoint = entrypoint

    @property
    def ray_serve_config(self):
        """Gets the ray_serve_config of this ProductionJobConfig.  # noqa: E501

        The Ray Serve config to use for this Production service. This config defines your Ray Serve application, and will be passed directly to Ray Serve. You can learn more about Ray Serve config files here: https://docs.ray.io/en/latest/serve/production-guide/config.html  # noqa: E501

        :return: The ray_serve_config of this ProductionJobConfig.  # noqa: E501
        :rtype: object
        """
        return self._ray_serve_config

    @ray_serve_config.setter
    def ray_serve_config(self, ray_serve_config):
        """Sets the ray_serve_config of this ProductionJobConfig.

        The Ray Serve config to use for this Production service. This config defines your Ray Serve application, and will be passed directly to Ray Serve. You can learn more about Ray Serve config files here: https://docs.ray.io/en/latest/serve/production-guide/config.html  # noqa: E501

        :param ray_serve_config: The ray_serve_config of this ProductionJobConfig.  # noqa: E501
        :type: object
        """

        self._ray_serve_config = ray_serve_config

    @property
    def runtime_env(self):
        """Gets the runtime_env of this ProductionJobConfig.  # noqa: E501

        A ray runtime env json. Your entrypoint will be run in the environment specified by this runtime env.  # noqa: E501

        :return: The runtime_env of this ProductionJobConfig.  # noqa: E501
        :rtype: RayRuntimeEnvConfig
        """
        return self._runtime_env

    @runtime_env.setter
    def runtime_env(self, runtime_env):
        """Sets the runtime_env of this ProductionJobConfig.

        A ray runtime env json. Your entrypoint will be run in the environment specified by this runtime env.  # noqa: E501

        :param runtime_env: The runtime_env of this ProductionJobConfig.  # noqa: E501
        :type: RayRuntimeEnvConfig
        """

        self._runtime_env = runtime_env

    @property
    def build_id(self):
        """Gets the build_id of this ProductionJobConfig.  # noqa: E501

        The id of the cluster env build. This id will determine the docker image your job is run on.  # noqa: E501

        :return: The build_id of this ProductionJobConfig.  # noqa: E501
        :rtype: str
        """
        return self._build_id

    @build_id.setter
    def build_id(self, build_id):
        """Sets the build_id of this ProductionJobConfig.

        The id of the cluster env build. This id will determine the docker image your job is run on.  # noqa: E501

        :param build_id: The build_id of this ProductionJobConfig.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and build_id is None:  # noqa: E501
            raise ValueError("Invalid value for `build_id`, must not be `None`")  # noqa: E501

        self._build_id = build_id

    @property
    def compute_config_id(self):
        """Gets the compute_config_id of this ProductionJobConfig.  # noqa: E501

        The id of the compute configuration that you want to use. This id will specify the resources required for your job  # noqa: E501

        :return: The compute_config_id of this ProductionJobConfig.  # noqa: E501
        :rtype: str
        """
        return self._compute_config_id

    @compute_config_id.setter
    def compute_config_id(self, compute_config_id):
        """Sets the compute_config_id of this ProductionJobConfig.

        The id of the compute configuration that you want to use. This id will specify the resources required for your job  # noqa: E501

        :param compute_config_id: The compute_config_id of this ProductionJobConfig.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and compute_config_id is None:  # noqa: E501
            raise ValueError("Invalid value for `compute_config_id`, must not be `None`")  # noqa: E501

        self._compute_config_id = compute_config_id

    @property
    def compute_config(self):
        """Gets the compute_config of this ProductionJobConfig.  # noqa: E501

        One-off compute that the cluster will use.  # noqa: E501

        :return: The compute_config of this ProductionJobConfig.  # noqa: E501
        :rtype: CreateClusterComputeConfig
        """
        return self._compute_config

    @compute_config.setter
    def compute_config(self, compute_config):
        """Sets the compute_config of this ProductionJobConfig.

        One-off compute that the cluster will use.  # noqa: E501

        :param compute_config: The compute_config of this ProductionJobConfig.  # noqa: E501
        :type: CreateClusterComputeConfig
        """

        self._compute_config = compute_config

    @property
    def max_retries(self):
        """Gets the max_retries of this ProductionJobConfig.  # noqa: E501

        The number of retries this job will attempt on failure. Set to None to set infinite retries  # noqa: E501

        :return: The max_retries of this ProductionJobConfig.  # noqa: E501
        :rtype: int
        """
        return self._max_retries

    @max_retries.setter
    def max_retries(self, max_retries):
        """Sets the max_retries of this ProductionJobConfig.

        The number of retries this job will attempt on failure. Set to None to set infinite retries  # noqa: E501

        :param max_retries: The max_retries of this ProductionJobConfig.  # noqa: E501
        :type: int
        """

        self._max_retries = max_retries

    @property
    def runtime_env_config(self):
        """Gets the runtime_env_config of this ProductionJobConfig.  # noqa: E501

        DEPRECATED: Use runtime_env  # noqa: E501

        :return: The runtime_env_config of this ProductionJobConfig.  # noqa: E501
        :rtype: RayRuntimeEnvConfig
        """
        return self._runtime_env_config

    @runtime_env_config.setter
    def runtime_env_config(self, runtime_env_config):
        """Sets the runtime_env_config of this ProductionJobConfig.

        DEPRECATED: Use runtime_env  # noqa: E501

        :param runtime_env_config: The runtime_env_config of this ProductionJobConfig.  # noqa: E501
        :type: RayRuntimeEnvConfig
        """

        self._runtime_env_config = runtime_env_config

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
        if not isinstance(other, ProductionJobConfig):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ProductionJobConfig):
            return True

        return self.to_dict() != other.to_dict()
