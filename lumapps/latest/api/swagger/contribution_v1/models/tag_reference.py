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

class TagReference(object):
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
        'type': 'str',
        'tag_id': 'str',
        'name': 'str'
    }

    attribute_map = {
        'type': 'type',
        'tag_id': 'tagId',
        'name': 'name'
    }

    def __init__(self, type=None, tag_id=None, name=None):  # noqa: E501
        """TagReference - a model defined in Swagger"""  # noqa: E501
        self._type = None
        self._tag_id = None
        self._name = None
        self.discriminator = None
        self.type = type
        self.tag_id = tag_id
        self.name = name

    @property
    def type(self):
        """Gets the type of this TagReference.  # noqa: E501

        The tag's type.  # noqa: E501

        :return: The type of this TagReference.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this TagReference.

        The tag's type.  # noqa: E501

        :param type: The type of this TagReference.  # noqa: E501
        :type: str
        """
        if type is None:
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501
        allowed_values = ["LEGACY", "FOLKSONOMY"]  # noqa: E501
        if type not in allowed_values:
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"  # noqa: E501
                .format(type, allowed_values)
            )

        self._type = type

    @property
    def tag_id(self):
        """Gets the tag_id of this TagReference.  # noqa: E501

        The tag's id.  # noqa: E501

        :return: The tag_id of this TagReference.  # noqa: E501
        :rtype: str
        """
        return self._tag_id

    @tag_id.setter
    def tag_id(self, tag_id):
        """Sets the tag_id of this TagReference.

        The tag's id.  # noqa: E501

        :param tag_id: The tag_id of this TagReference.  # noqa: E501
        :type: str
        """
        if tag_id is None:
            raise ValueError("Invalid value for `tag_id`, must not be `None`")  # noqa: E501

        self._tag_id = tag_id

    @property
    def name(self):
        """Gets the name of this TagReference.  # noqa: E501

        The tag's name.  # noqa: E501

        :return: The name of this TagReference.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this TagReference.

        The tag's name.  # noqa: E501

        :param name: The name of this TagReference.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

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
        if issubclass(TagReference, dict):
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
        if not isinstance(other, TagReference):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
