# coding: utf-8

"""
    CMS Contribution API

    The CMS Contribution API allows access and modification of Lumapps contents.   # noqa: E501

    OpenAPI spec version: 0.1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class ContainerReference(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'container_type': 'ContainerType',
        'container_id': 'str'
    }

    attribute_map = {
        'container_type': 'containerType',
        'container_id': 'containerId'
    }

    def __init__(self, container_type=None, container_id=None):  # noqa: E501
        """ContainerReference - a model defined in Swagger"""  # noqa: E501
        self._container_type = None
        self._container_id = None
        self.discriminator = None
        self.container_type = container_type
        self.container_id = container_id

    @property
    def container_type(self):
        """Gets the container_type of this ContainerReference.  # noqa: E501


        :return: The container_type of this ContainerReference.  # noqa: E501
        :rtype: ContainerType
        """
        return self._container_type

    @container_type.setter
    def container_type(self, container_type):
        """Sets the container_type of this ContainerReference.


        :param container_type: The container_type of this ContainerReference.  # noqa: E501
        :type: ContainerType
        """
        if container_type is None:
            raise ValueError("Invalid value for `container_type`, must not be `None`")  # noqa: E501

        self._container_type = container_type

    @property
    def container_id(self):
        """Gets the container_id of this ContainerReference.  # noqa: E501

        The container's id  # noqa: E501

        :return: The container_id of this ContainerReference.  # noqa: E501
        :rtype: str
        """
        return self._container_id

    @container_id.setter
    def container_id(self, container_id):
        """Sets the container_id of this ContainerReference.

        The container's id  # noqa: E501

        :param container_id: The container_id of this ContainerReference.  # noqa: E501
        :type: str
        """
        if container_id is None:
            raise ValueError("Invalid value for `container_id`, must not be `None`")  # noqa: E501

        self._container_id = container_id

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
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
        if issubclass(ContainerReference, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ContainerReference):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
