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


class ImportAicaModel(object):
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
        'model_object_storage_uri': 'str',
        'generation_configuration_json': 'object',
        'params_size_in_billions': 'int',
        'cloud_id': 'str'
    }

    attribute_map = {
        'id': 'id',
        'model_object_storage_uri': 'model_object_storage_uri',
        'generation_configuration_json': 'generation_configuration_json',
        'params_size_in_billions': 'params_size_in_billions',
        'cloud_id': 'cloud_id'
    }

    def __init__(self, id=None, model_object_storage_uri=None, generation_configuration_json=None, params_size_in_billions=None, cloud_id=None, local_vars_configuration=None):  # noqa: E501
        """ImportAicaModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._model_object_storage_uri = None
        self._generation_configuration_json = None
        self._params_size_in_billions = None
        self._cloud_id = None
        self.discriminator = None

        self.id = id
        if model_object_storage_uri is not None:
            self.model_object_storage_uri = model_object_storage_uri
        self.generation_configuration_json = generation_configuration_json
        self.params_size_in_billions = params_size_in_billions
        self.cloud_id = cloud_id

    @property
    def id(self):
        """Gets the id of this ImportAicaModel.  # noqa: E501

        Name of the model to be imported.  # noqa: E501

        :return: The id of this ImportAicaModel.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this ImportAicaModel.

        Name of the model to be imported.  # noqa: E501

        :param id: The id of this ImportAicaModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def model_object_storage_uri(self):
        """Gets the model_object_storage_uri of this ImportAicaModel.  # noqa: E501

        The URI of the model object in the object storage.  # noqa: E501

        :return: The model_object_storage_uri of this ImportAicaModel.  # noqa: E501
        :rtype: str
        """
        return self._model_object_storage_uri

    @model_object_storage_uri.setter
    def model_object_storage_uri(self, model_object_storage_uri):
        """Sets the model_object_storage_uri of this ImportAicaModel.

        The URI of the model object in the object storage.  # noqa: E501

        :param model_object_storage_uri: The model_object_storage_uri of this ImportAicaModel.  # noqa: E501
        :type: str
        """

        self._model_object_storage_uri = model_object_storage_uri

    @property
    def generation_configuration_json(self):
        """Gets the generation_configuration_json of this ImportAicaModel.  # noqa: E501

        The configuration for the generation section.  # noqa: E501

        :return: The generation_configuration_json of this ImportAicaModel.  # noqa: E501
        :rtype: object
        """
        return self._generation_configuration_json

    @generation_configuration_json.setter
    def generation_configuration_json(self, generation_configuration_json):
        """Sets the generation_configuration_json of this ImportAicaModel.

        The configuration for the generation section.  # noqa: E501

        :param generation_configuration_json: The generation_configuration_json of this ImportAicaModel.  # noqa: E501
        :type: object
        """
        if self.local_vars_configuration.client_side_validation and generation_configuration_json is None:  # noqa: E501
            raise ValueError("Invalid value for `generation_configuration_json`, must not be `None`")  # noqa: E501

        self._generation_configuration_json = generation_configuration_json

    @property
    def params_size_in_billions(self):
        """Gets the params_size_in_billions of this ImportAicaModel.  # noqa: E501

        User provided model parameter size in billions. This value will be used to provide the default rayllm serving configurations of the model.  # noqa: E501

        :return: The params_size_in_billions of this ImportAicaModel.  # noqa: E501
        :rtype: int
        """
        return self._params_size_in_billions

    @params_size_in_billions.setter
    def params_size_in_billions(self, params_size_in_billions):
        """Sets the params_size_in_billions of this ImportAicaModel.

        User provided model parameter size in billions. This value will be used to provide the default rayllm serving configurations of the model.  # noqa: E501

        :param params_size_in_billions: The params_size_in_billions of this ImportAicaModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and params_size_in_billions is None:  # noqa: E501
            raise ValueError("Invalid value for `params_size_in_billions`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                params_size_in_billions is not None and params_size_in_billions < 0):  # noqa: E501
            raise ValueError("Invalid value for `params_size_in_billions`, must be a value greater than or equal to `0`")  # noqa: E501

        self._params_size_in_billions = params_size_in_billions

    @property
    def cloud_id(self):
        """Gets the cloud_id of this ImportAicaModel.  # noqa: E501

        The cloud id for the model.  # noqa: E501

        :return: The cloud_id of this ImportAicaModel.  # noqa: E501
        :rtype: str
        """
        return self._cloud_id

    @cloud_id.setter
    def cloud_id(self, cloud_id):
        """Sets the cloud_id of this ImportAicaModel.

        The cloud id for the model.  # noqa: E501

        :param cloud_id: The cloud_id of this ImportAicaModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and cloud_id is None:  # noqa: E501
            raise ValueError("Invalid value for `cloud_id`, must not be `None`")  # noqa: E501

        self._cloud_id = cloud_id

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
        if not isinstance(other, ImportAicaModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ImportAicaModel):
            return True

        return self.to_dict() != other.to_dict()
