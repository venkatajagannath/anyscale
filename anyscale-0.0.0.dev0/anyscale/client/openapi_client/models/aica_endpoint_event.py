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


class AicaEndpointEvent(object):
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
        'service_event_id': 'str',
        'aica_endpoint_id': 'str',
        'timestamp': 'datetime',
        'event_type': 'AicaEndpointEventType',
        'level': 'AicaEndpointEventLevel',
        'scope': 'AicaEndpointScope',
        'message': 'str',
        'cluster_event_id': 'str',
        'cluster_state_transition_id': 'str',
        'serve_deployment_event_id': 'str',
        'model_name': 'str'
    }

    attribute_map = {
        'id': 'id',
        'service_event_id': 'service_event_id',
        'aica_endpoint_id': 'aica_endpoint_id',
        'timestamp': 'timestamp',
        'event_type': 'event_type',
        'level': 'level',
        'scope': 'scope',
        'message': 'message',
        'cluster_event_id': 'cluster_event_id',
        'cluster_state_transition_id': 'cluster_state_transition_id',
        'serve_deployment_event_id': 'serve_deployment_event_id',
        'model_name': 'model_name'
    }

    def __init__(self, id=None, service_event_id=None, aica_endpoint_id=None, timestamp=None, event_type=None, level=None, scope=None, message=None, cluster_event_id=None, cluster_state_transition_id=None, serve_deployment_event_id=None, model_name=None, local_vars_configuration=None):  # noqa: E501
        """AicaEndpointEvent - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._service_event_id = None
        self._aica_endpoint_id = None
        self._timestamp = None
        self._event_type = None
        self._level = None
        self._scope = None
        self._message = None
        self._cluster_event_id = None
        self._cluster_state_transition_id = None
        self._serve_deployment_event_id = None
        self._model_name = None
        self.discriminator = None

        self.id = id
        if service_event_id is not None:
            self.service_event_id = service_event_id
        self.aica_endpoint_id = aica_endpoint_id
        self.timestamp = timestamp
        if event_type is not None:
            self.event_type = event_type
        self.level = level
        self.scope = scope
        if message is not None:
            self.message = message
        if cluster_event_id is not None:
            self.cluster_event_id = cluster_event_id
        if cluster_state_transition_id is not None:
            self.cluster_state_transition_id = cluster_state_transition_id
        if serve_deployment_event_id is not None:
            self.serve_deployment_event_id = serve_deployment_event_id
        if model_name is not None:
            self.model_name = model_name

    @property
    def id(self):
        """Gets the id of this AicaEndpointEvent.  # noqa: E501

        Id of the AICA endpoint event.  # noqa: E501

        :return: The id of this AicaEndpointEvent.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this AicaEndpointEvent.

        Id of the AICA endpoint event.  # noqa: E501

        :param id: The id of this AicaEndpointEvent.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def service_event_id(self):
        """Gets the service_event_id of this AicaEndpointEvent.  # noqa: E501

        Service event this AICA endpoint event is based off.  # noqa: E501

        :return: The service_event_id of this AicaEndpointEvent.  # noqa: E501
        :rtype: str
        """
        return self._service_event_id

    @service_event_id.setter
    def service_event_id(self, service_event_id):
        """Sets the service_event_id of this AicaEndpointEvent.

        Service event this AICA endpoint event is based off.  # noqa: E501

        :param service_event_id: The service_event_id of this AicaEndpointEvent.  # noqa: E501
        :type: str
        """

        self._service_event_id = service_event_id

    @property
    def aica_endpoint_id(self):
        """Gets the aica_endpoint_id of this AicaEndpointEvent.  # noqa: E501

        Id of AICA endpoint this event belongs to.  # noqa: E501

        :return: The aica_endpoint_id of this AicaEndpointEvent.  # noqa: E501
        :rtype: str
        """
        return self._aica_endpoint_id

    @aica_endpoint_id.setter
    def aica_endpoint_id(self, aica_endpoint_id):
        """Sets the aica_endpoint_id of this AicaEndpointEvent.

        Id of AICA endpoint this event belongs to.  # noqa: E501

        :param aica_endpoint_id: The aica_endpoint_id of this AicaEndpointEvent.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and aica_endpoint_id is None:  # noqa: E501
            raise ValueError("Invalid value for `aica_endpoint_id`, must not be `None`")  # noqa: E501

        self._aica_endpoint_id = aica_endpoint_id

    @property
    def timestamp(self):
        """Gets the timestamp of this AicaEndpointEvent.  # noqa: E501

        Inserted at time of service event this AICA endpoint event is based off.  # noqa: E501

        :return: The timestamp of this AicaEndpointEvent.  # noqa: E501
        :rtype: datetime
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this AicaEndpointEvent.

        Inserted at time of service event this AICA endpoint event is based off.  # noqa: E501

        :param timestamp: The timestamp of this AicaEndpointEvent.  # noqa: E501
        :type: datetime
        """
        if self.local_vars_configuration.client_side_validation and timestamp is None:  # noqa: E501
            raise ValueError("Invalid value for `timestamp`, must not be `None`")  # noqa: E501

        self._timestamp = timestamp

    @property
    def event_type(self):
        """Gets the event_type of this AicaEndpointEvent.  # noqa: E501

        Type of AICA endpoint event.  # noqa: E501

        :return: The event_type of this AicaEndpointEvent.  # noqa: E501
        :rtype: AicaEndpointEventType
        """
        return self._event_type

    @event_type.setter
    def event_type(self, event_type):
        """Sets the event_type of this AicaEndpointEvent.

        Type of AICA endpoint event.  # noqa: E501

        :param event_type: The event_type of this AicaEndpointEvent.  # noqa: E501
        :type: AicaEndpointEventType
        """

        self._event_type = event_type

    @property
    def level(self):
        """Gets the level of this AicaEndpointEvent.  # noqa: E501

        Log level of AICA endpoint event.  # noqa: E501

        :return: The level of this AicaEndpointEvent.  # noqa: E501
        :rtype: AicaEndpointEventLevel
        """
        return self._level

    @level.setter
    def level(self, level):
        """Sets the level of this AicaEndpointEvent.

        Log level of AICA endpoint event.  # noqa: E501

        :param level: The level of this AicaEndpointEvent.  # noqa: E501
        :type: AicaEndpointEventLevel
        """
        if self.local_vars_configuration.client_side_validation and level is None:  # noqa: E501
            raise ValueError("Invalid value for `level`, must not be `None`")  # noqa: E501

        self._level = level

    @property
    def scope(self):
        """Gets the scope of this AicaEndpointEvent.  # noqa: E501

        Scope of AICA endpoint event.  # noqa: E501

        :return: The scope of this AicaEndpointEvent.  # noqa: E501
        :rtype: AicaEndpointScope
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """Sets the scope of this AicaEndpointEvent.

        Scope of AICA endpoint event.  # noqa: E501

        :param scope: The scope of this AicaEndpointEvent.  # noqa: E501
        :type: AicaEndpointScope
        """
        if self.local_vars_configuration.client_side_validation and scope is None:  # noqa: E501
            raise ValueError("Invalid value for `scope`, must not be `None`")  # noqa: E501

        self._scope = scope

    @property
    def message(self):
        """Gets the message of this AicaEndpointEvent.  # noqa: E501


        :return: The message of this AicaEndpointEvent.  # noqa: E501
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this AicaEndpointEvent.


        :param message: The message of this AicaEndpointEvent.  # noqa: E501
        :type: str
        """

        self._message = message

    @property
    def cluster_event_id(self):
        """Gets the cluster_event_id of this AicaEndpointEvent.  # noqa: E501

        Cluster event id this AICA endpoint event is based off.   # noqa: E501

        :return: The cluster_event_id of this AicaEndpointEvent.  # noqa: E501
        :rtype: str
        """
        return self._cluster_event_id

    @cluster_event_id.setter
    def cluster_event_id(self, cluster_event_id):
        """Sets the cluster_event_id of this AicaEndpointEvent.

        Cluster event id this AICA endpoint event is based off.   # noqa: E501

        :param cluster_event_id: The cluster_event_id of this AicaEndpointEvent.  # noqa: E501
        :type: str
        """

        self._cluster_event_id = cluster_event_id

    @property
    def cluster_state_transition_id(self):
        """Gets the cluster_state_transition_id of this AicaEndpointEvent.  # noqa: E501

        Cluster state transition id this AICA endpoint event is based off.   # noqa: E501

        :return: The cluster_state_transition_id of this AicaEndpointEvent.  # noqa: E501
        :rtype: str
        """
        return self._cluster_state_transition_id

    @cluster_state_transition_id.setter
    def cluster_state_transition_id(self, cluster_state_transition_id):
        """Sets the cluster_state_transition_id of this AicaEndpointEvent.

        Cluster state transition id this AICA endpoint event is based off.   # noqa: E501

        :param cluster_state_transition_id: The cluster_state_transition_id of this AicaEndpointEvent.  # noqa: E501
        :type: str
        """

        self._cluster_state_transition_id = cluster_state_transition_id

    @property
    def serve_deployment_event_id(self):
        """Gets the serve_deployment_event_id of this AicaEndpointEvent.  # noqa: E501

        Serve deployment event id this AICA endpoint event is based off.   # noqa: E501

        :return: The serve_deployment_event_id of this AicaEndpointEvent.  # noqa: E501
        :rtype: str
        """
        return self._serve_deployment_event_id

    @serve_deployment_event_id.setter
    def serve_deployment_event_id(self, serve_deployment_event_id):
        """Sets the serve_deployment_event_id of this AicaEndpointEvent.

        Serve deployment event id this AICA endpoint event is based off.   # noqa: E501

        :param serve_deployment_event_id: The serve_deployment_event_id of this AicaEndpointEvent.  # noqa: E501
        :type: str
        """

        self._serve_deployment_event_id = serve_deployment_event_id

    @property
    def model_name(self):
        """Gets the model_name of this AicaEndpointEvent.  # noqa: E501

        Model name if this AICA endpoint event refers to a model event.   # noqa: E501

        :return: The model_name of this AicaEndpointEvent.  # noqa: E501
        :rtype: str
        """
        return self._model_name

    @model_name.setter
    def model_name(self, model_name):
        """Sets the model_name of this AicaEndpointEvent.

        Model name if this AICA endpoint event refers to a model event.   # noqa: E501

        :param model_name: The model_name of this AicaEndpointEvent.  # noqa: E501
        :type: str
        """

        self._model_name = model_name

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
        if not isinstance(other, AicaEndpointEvent):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AicaEndpointEvent):
            return True

        return self.to_dict() != other.to_dict()
