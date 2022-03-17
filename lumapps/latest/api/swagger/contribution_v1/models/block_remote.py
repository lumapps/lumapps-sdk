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
from .base_block import BaseBlock  # noqa: F401,E501

class BlockRemote(BaseBlock):
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
        'extension_id': 'str',
        'extension_properties': 'object',
        'global_properties': 'object',
        'bundle_url': 'str'
    }
    if hasattr(BaseBlock, "swagger_types"):
        swagger_types.update(BaseBlock.swagger_types)

    attribute_map = {
        'extension_id': 'extensionId',
        'extension_properties': 'extensionProperties',
        'global_properties': 'globalProperties',
        'bundle_url': 'bundleUrl'
    }
    if hasattr(BaseBlock, "attribute_map"):
        attribute_map.update(BaseBlock.attribute_map)

    def __init__(self, extension_id=None, extension_properties=None, global_properties=None, bundle_url=None, *args, **kwargs):  # noqa: E501
        """BlockRemote - a model defined in Swagger"""  # noqa: E501
        self._extension_id = None
        self._extension_properties = None
        self._global_properties = None
        self._bundle_url = None
        self.discriminator = None
        self.extension_id = extension_id
        self.extension_properties = extension_properties
        if global_properties is not None:
            self.global_properties = global_properties
        if bundle_url is not None:
            self.bundle_url = bundle_url
        BaseBlock.__init__(self, *args, **kwargs)

    @property
    def extension_id(self):
        """Gets the extension_id of this BlockRemote.  # noqa: E501

        The extension's id.  # noqa: E501

        :return: The extension_id of this BlockRemote.  # noqa: E501
        :rtype: str
        """
        return self._extension_id

    @extension_id.setter
    def extension_id(self, extension_id):
        """Sets the extension_id of this BlockRemote.

        The extension's id.  # noqa: E501

        :param extension_id: The extension_id of this BlockRemote.  # noqa: E501
        :type: str
        """
        if extension_id is None:
            raise ValueError("Invalid value for `extension_id`, must not be `None`")  # noqa: E501

        self._extension_id = extension_id

    @property
    def extension_properties(self):
        """Gets the extension_properties of this BlockRemote.  # noqa: E501

        The properties configured for this extension.  # noqa: E501

        :return: The extension_properties of this BlockRemote.  # noqa: E501
        :rtype: object
        """
        return self._extension_properties

    @extension_properties.setter
    def extension_properties(self, extension_properties):
        """Sets the extension_properties of this BlockRemote.

        The properties configured for this extension.  # noqa: E501

        :param extension_properties: The extension_properties of this BlockRemote.  # noqa: E501
        :type: object
        """
        if extension_properties is None:
            raise ValueError("Invalid value for `extension_properties`, must not be `None`")  # noqa: E501

        self._extension_properties = extension_properties

    @property
    def global_properties(self):
        """Gets the global_properties of this BlockRemote.  # noqa: E501

        The extension's settings that apply all its widgets.  # noqa: E501

        :return: The global_properties of this BlockRemote.  # noqa: E501
        :rtype: object
        """
        return self._global_properties

    @global_properties.setter
    def global_properties(self, global_properties):
        """Sets the global_properties of this BlockRemote.

        The extension's settings that apply all its widgets.  # noqa: E501

        :param global_properties: The global_properties of this BlockRemote.  # noqa: E501
        :type: object
        """

        self._global_properties = global_properties

    @property
    def bundle_url(self):
        """Gets the bundle_url of this BlockRemote.  # noqa: E501

        The URL to download the extension's bundle.  # noqa: E501

        :return: The bundle_url of this BlockRemote.  # noqa: E501
        :rtype: str
        """
        return self._bundle_url

    @bundle_url.setter
    def bundle_url(self, bundle_url):
        """Sets the bundle_url of this BlockRemote.

        The URL to download the extension's bundle.  # noqa: E501

        :param bundle_url: The bundle_url of this BlockRemote.  # noqa: E501
        :type: str
        """

        self._bundle_url = bundle_url

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
        if issubclass(BlockRemote, dict):
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
        if not isinstance(other, BlockRemote):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
