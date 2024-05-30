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


class ClusterOperation(object):
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
        'completed': 'bool',
        'progress': 'OperationProgress',
        'result': 'OperationResult',
        'cluster_id': 'str',
        'cluster_operation_type': 'ClusterOperationType'
    }

    attribute_map = {
        'id': 'id',
        'completed': 'completed',
        'progress': 'progress',
        'result': 'result',
        'cluster_id': 'cluster_id',
        'cluster_operation_type': 'cluster_operation_type'
    }

    def __init__(self, id=None, completed=None, progress=None, result=None, cluster_id=None, cluster_operation_type=None, local_vars_configuration=None):  # noqa: E501
        """ClusterOperation - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._completed = None
        self._progress = None
        self._result = None
        self._cluster_id = None
        self._cluster_operation_type = None
        self.discriminator = None

        self.id = id
        self.completed = completed
        if progress is not None:
            self.progress = progress
        if result is not None:
            self.result = result
        self.cluster_id = cluster_id
        self.cluster_operation_type = cluster_operation_type

    @property
    def id(self):
        """Gets the id of this ClusterOperation.  # noqa: E501

        ID of this operation.  # noqa: E501

        :return: The id of this ClusterOperation.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this ClusterOperation.

        ID of this operation.  # noqa: E501

        :param id: The id of this ClusterOperation.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def completed(self):
        """Gets the completed of this ClusterOperation.  # noqa: E501

        Boolean indicating if this operation is completed.  # noqa: E501

        :return: The completed of this ClusterOperation.  # noqa: E501
        :rtype: bool
        """
        return self._completed

    @completed.setter
    def completed(self, completed):
        """Sets the completed of this ClusterOperation.

        Boolean indicating if this operation is completed.  # noqa: E501

        :param completed: The completed of this ClusterOperation.  # noqa: E501
        :type: bool
        """
        if self.local_vars_configuration.client_side_validation and completed is None:  # noqa: E501
            raise ValueError("Invalid value for `completed`, must not be `None`")  # noqa: E501

        self._completed = completed

    @property
    def progress(self):
        """Gets the progress of this ClusterOperation.  # noqa: E501

        Details about the progress of this operation at the time of the request.             This will be absent for completed operations.  # noqa: E501

        :return: The progress of this ClusterOperation.  # noqa: E501
        :rtype: OperationProgress
        """
        return self._progress

    @progress.setter
    def progress(self, progress):
        """Sets the progress of this ClusterOperation.

        Details about the progress of this operation at the time of the request.             This will be absent for completed operations.  # noqa: E501

        :param progress: The progress of this ClusterOperation.  # noqa: E501
        :type: OperationProgress
        """

        self._progress = progress

    @property
    def result(self):
        """Gets the result of this ClusterOperation.  # noqa: E501

        The result of this operation after it has completed.             This is always provided when the operation is complete.  # noqa: E501

        :return: The result of this ClusterOperation.  # noqa: E501
        :rtype: OperationResult
        """
        return self._result

    @result.setter
    def result(self, result):
        """Sets the result of this ClusterOperation.

        The result of this operation after it has completed.             This is always provided when the operation is complete.  # noqa: E501

        :param result: The result of this ClusterOperation.  # noqa: E501
        :type: OperationResult
        """

        self._result = result

    @property
    def cluster_id(self):
        """Gets the cluster_id of this ClusterOperation.  # noqa: E501

        ID of the Cluster that is being updated.  # noqa: E501

        :return: The cluster_id of this ClusterOperation.  # noqa: E501
        :rtype: str
        """
        return self._cluster_id

    @cluster_id.setter
    def cluster_id(self, cluster_id):
        """Sets the cluster_id of this ClusterOperation.

        ID of the Cluster that is being updated.  # noqa: E501

        :param cluster_id: The cluster_id of this ClusterOperation.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and cluster_id is None:  # noqa: E501
            raise ValueError("Invalid value for `cluster_id`, must not be `None`")  # noqa: E501

        self._cluster_id = cluster_id

    @property
    def cluster_operation_type(self):
        """Gets the cluster_operation_type of this ClusterOperation.  # noqa: E501

        The variety of operation being performed:             start sets the Cluster's goal state to Running,             terminate sets the Cluster's goal state to Terminated  # noqa: E501

        :return: The cluster_operation_type of this ClusterOperation.  # noqa: E501
        :rtype: ClusterOperationType
        """
        return self._cluster_operation_type

    @cluster_operation_type.setter
    def cluster_operation_type(self, cluster_operation_type):
        """Sets the cluster_operation_type of this ClusterOperation.

        The variety of operation being performed:             start sets the Cluster's goal state to Running,             terminate sets the Cluster's goal state to Terminated  # noqa: E501

        :param cluster_operation_type: The cluster_operation_type of this ClusterOperation.  # noqa: E501
        :type: ClusterOperationType
        """
        if self.local_vars_configuration.client_side_validation and cluster_operation_type is None:  # noqa: E501
            raise ValueError("Invalid value for `cluster_operation_type`, must not be `None`")  # noqa: E501

        self._cluster_operation_type = cluster_operation_type

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
        if not isinstance(other, ClusterOperation):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ClusterOperation):
            return True

        return self.to_dict() != other.to_dict()
