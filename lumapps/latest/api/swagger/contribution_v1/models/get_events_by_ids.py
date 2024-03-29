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


class GetEventsByIds(object):
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
        "items": "list[Event]",
        "more": "bool",
        "cursor": "str",
        "errors": "GetByIdErrors",
    }

    attribute_map = {
        "items": "items",
        "more": "more",
        "cursor": "cursor",
        "errors": "errors",
    }

    def __init__(self, items=None, more=None, cursor=None, errors=None):  # noqa: E501
        """GetEventsByIds - a model defined in Swagger"""  # noqa: E501
        self._items = None
        self._more = None
        self._cursor = None
        self._errors = None
        self.discriminator = None
        if items is not None:
            self.items = items
        if more is not None:
            self.more = more
        if cursor is not None:
            self.cursor = cursor
        if errors is not None:
            self.errors = errors

    @property
    def items(self):
        """Gets the items of this GetEventsByIds.  # noqa: E501

        The events  # noqa: E501

        :return: The items of this GetEventsByIds.  # noqa: E501
        :rtype: list[Event]
        """
        return self._items

    @items.setter
    def items(self, items):
        """Sets the items of this GetEventsByIds.

        The events  # noqa: E501

        :param items: The items of this GetEventsByIds.  # noqa: E501
        :type: list[Event]
        """

        self._items = items

    @property
    def more(self):
        """Gets the more of this GetEventsByIds.  # noqa: E501

        Whether there is more events to load.  # noqa: E501

        :return: The more of this GetEventsByIds.  # noqa: E501
        :rtype: bool
        """
        return self._more

    @more.setter
    def more(self, more):
        """Sets the more of this GetEventsByIds.

        Whether there is more events to load.  # noqa: E501

        :param more: The more of this GetEventsByIds.  # noqa: E501
        :type: bool
        """

        self._more = more

    @property
    def cursor(self):
        """Gets the cursor of this GetEventsByIds.  # noqa: E501

        The cursor for loading more events, if any.  # noqa: E501

        :return: The cursor of this GetEventsByIds.  # noqa: E501
        :rtype: str
        """
        return self._cursor

    @cursor.setter
    def cursor(self, cursor):
        """Sets the cursor of this GetEventsByIds.

        The cursor for loading more events, if any.  # noqa: E501

        :param cursor: The cursor of this GetEventsByIds.  # noqa: E501
        :type: str
        """

        self._cursor = cursor

    @property
    def errors(self):
        """Gets the errors of this GetEventsByIds.  # noqa: E501


        :return: The errors of this GetEventsByIds.  # noqa: E501
        :rtype: GetByIdErrors
        """
        return self._errors

    @errors.setter
    def errors(self, errors):
        """Sets the errors of this GetEventsByIds.


        :param errors: The errors of this GetEventsByIds.  # noqa: E501
        :type: GetByIdErrors
        """

        self._errors = errors

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(
                    map(lambda x: x.to_dict() if hasattr(x, "to_dict") else x, value)
                )
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(
                    map(
                        lambda item: (item[0], item[1].to_dict())
                        if hasattr(item[1], "to_dict")
                        else item,
                        value.items(),
                    )
                )
            else:
                result[attr] = value
        if issubclass(GetEventsByIds, dict):
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
        if not isinstance(other, GetEventsByIds):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
