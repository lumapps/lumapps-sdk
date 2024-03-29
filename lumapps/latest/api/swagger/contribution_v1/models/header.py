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


class Header(object):
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
        "label": "str",
        "label_key": "str",
        "icon": "str",
        "style": "ElementStyle",
    }

    attribute_map = {
        "label": "label",
        "label_key": "labelKey",
        "icon": "icon",
        "style": "style",
    }

    def __init__(self, label=None, label_key=None, icon=None, style=None):  # noqa: E501
        """Header - a model defined in Swagger"""  # noqa: E501
        self._label = None
        self._label_key = None
        self._icon = None
        self._style = None
        self.discriminator = None
        if label is not None:
            self.label = label
        if label_key is not None:
            self.label_key = label_key
        if icon is not None:
            self.icon = icon
        if style is not None:
            self.style = style

    @property
    def label(self):
        """Gets the label of this Header.  # noqa: E501

        The header's text.  # noqa: E501

        :return: The label of this Header.  # noqa: E501
        :rtype: str
        """
        return self._label

    @label.setter
    def label(self, label):
        """Sets the label of this Header.

        The header's text.  # noqa: E501

        :param label: The label of this Header.  # noqa: E501
        :type: str
        """

        self._label = label

    @property
    def label_key(self):
        """Gets the label_key of this Header.  # noqa: E501

        The translation key to use for this header. Note:   If present, this takes precedence over any value present in the label field.   # noqa: E501

        :return: The label_key of this Header.  # noqa: E501
        :rtype: str
        """
        return self._label_key

    @label_key.setter
    def label_key(self, label_key):
        """Sets the label_key of this Header.

        The translation key to use for this header. Note:   If present, this takes precedence over any value present in the label field.   # noqa: E501

        :param label_key: The label_key of this Header.  # noqa: E501
        :type: str
        """

        self._label_key = label_key

    @property
    def icon(self):
        """Gets the icon of this Header.  # noqa: E501

        The header's icon.  # noqa: E501

        :return: The icon of this Header.  # noqa: E501
        :rtype: str
        """
        return self._icon

    @icon.setter
    def icon(self, icon):
        """Sets the icon of this Header.

        The header's icon.  # noqa: E501

        :param icon: The icon of this Header.  # noqa: E501
        :type: str
        """

        self._icon = icon

    @property
    def style(self):
        """Gets the style of this Header.  # noqa: E501


        :return: The style of this Header.  # noqa: E501
        :rtype: ElementStyle
        """
        return self._style

    @style.setter
    def style(self, style):
        """Sets the style of this Header.


        :param style: The style of this Header.  # noqa: E501
        :type: ElementStyle
        """

        self._style = style

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
        if issubclass(Header, dict):
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
        if not isinstance(other, Header):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
