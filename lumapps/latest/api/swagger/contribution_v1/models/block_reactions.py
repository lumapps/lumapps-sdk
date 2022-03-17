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

class BlockReactions(BaseBlock):
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
        'resource_type': 'str',
        'resource_id': 'str',
        'likes': 'int',
        'is_liked': 'bool',
        'comments': 'int',
        'is_comment_count_visible': 'bool'
    }
    if hasattr(BaseBlock, "swagger_types"):
        swagger_types.update(BaseBlock.swagger_types)

    attribute_map = {
        'resource_type': 'resourceType',
        'resource_id': 'resourceId',
        'likes': 'likes',
        'is_liked': 'isLiked',
        'comments': 'comments',
        'is_comment_count_visible': 'isCommentCountVisible'
    }
    if hasattr(BaseBlock, "attribute_map"):
        attribute_map.update(BaseBlock.attribute_map)

    def __init__(self, resource_type=None, resource_id=None, likes=None, is_liked=None, comments=None, is_comment_count_visible=None, *args, **kwargs):  # noqa: E501
        """BlockReactions - a model defined in Swagger"""  # noqa: E501
        self._resource_type = None
        self._resource_id = None
        self._likes = None
        self._is_liked = None
        self._comments = None
        self._is_comment_count_visible = None
        self.discriminator = None
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.likes = likes
        self.is_liked = is_liked
        self.comments = comments
        self.is_comment_count_visible = is_comment_count_visible
        BaseBlock.__init__(self, *args, **kwargs)

    @property
    def resource_type(self):
        """Gets the resource_type of this BlockReactions.  # noqa: E501

        The type of the associated resource.  # noqa: E501

        :return: The resource_type of this BlockReactions.  # noqa: E501
        :rtype: str
        """
        return self._resource_type

    @resource_type.setter
    def resource_type(self, resource_type):
        """Sets the resource_type of this BlockReactions.

        The type of the associated resource.  # noqa: E501

        :param resource_type: The resource_type of this BlockReactions.  # noqa: E501
        :type: str
        """
        if resource_type is None:
            raise ValueError("Invalid value for `resource_type`, must not be `None`")  # noqa: E501

        self._resource_type = resource_type

    @property
    def resource_id(self):
        """Gets the resource_id of this BlockReactions.  # noqa: E501

        The id of the associated resource.  # noqa: E501

        :return: The resource_id of this BlockReactions.  # noqa: E501
        :rtype: str
        """
        return self._resource_id

    @resource_id.setter
    def resource_id(self, resource_id):
        """Sets the resource_id of this BlockReactions.

        The id of the associated resource.  # noqa: E501

        :param resource_id: The resource_id of this BlockReactions.  # noqa: E501
        :type: str
        """
        if resource_id is None:
            raise ValueError("Invalid value for `resource_id`, must not be `None`")  # noqa: E501

        self._resource_id = resource_id

    @property
    def likes(self):
        """Gets the likes of this BlockReactions.  # noqa: E501

        The number of likes for the associated resource.  # noqa: E501

        :return: The likes of this BlockReactions.  # noqa: E501
        :rtype: int
        """
        return self._likes

    @likes.setter
    def likes(self, likes):
        """Sets the likes of this BlockReactions.

        The number of likes for the associated resource.  # noqa: E501

        :param likes: The likes of this BlockReactions.  # noqa: E501
        :type: int
        """
        if likes is None:
            raise ValueError("Invalid value for `likes`, must not be `None`")  # noqa: E501

        self._likes = likes

    @property
    def is_liked(self):
        """Gets the is_liked of this BlockReactions.  # noqa: E501

        Whether the current user has liked the associated resource.  # noqa: E501

        :return: The is_liked of this BlockReactions.  # noqa: E501
        :rtype: bool
        """
        return self._is_liked

    @is_liked.setter
    def is_liked(self, is_liked):
        """Sets the is_liked of this BlockReactions.

        Whether the current user has liked the associated resource.  # noqa: E501

        :param is_liked: The is_liked of this BlockReactions.  # noqa: E501
        :type: bool
        """
        if is_liked is None:
            raise ValueError("Invalid value for `is_liked`, must not be `None`")  # noqa: E501

        self._is_liked = is_liked

    @property
    def comments(self):
        """Gets the comments of this BlockReactions.  # noqa: E501

        The number of comments for the associated resource.  # noqa: E501

        :return: The comments of this BlockReactions.  # noqa: E501
        :rtype: int
        """
        return self._comments

    @comments.setter
    def comments(self, comments):
        """Sets the comments of this BlockReactions.

        The number of comments for the associated resource.  # noqa: E501

        :param comments: The comments of this BlockReactions.  # noqa: E501
        :type: int
        """
        if comments is None:
            raise ValueError("Invalid value for `comments`, must not be `None`")  # noqa: E501

        self._comments = comments

    @property
    def is_comment_count_visible(self):
        """Gets the is_comment_count_visible of this BlockReactions.  # noqa: E501

        Whether the comment count has visible for the associated resource.  # noqa: E501

        :return: The is_comment_count_visible of this BlockReactions.  # noqa: E501
        :rtype: bool
        """
        return self._is_comment_count_visible

    @is_comment_count_visible.setter
    def is_comment_count_visible(self, is_comment_count_visible):
        """Sets the is_comment_count_visible of this BlockReactions.

        Whether the comment count has visible for the associated resource.  # noqa: E501

        :param is_comment_count_visible: The is_comment_count_visible of this BlockReactions.  # noqa: E501
        :type: bool
        """
        if is_comment_count_visible is None:
            raise ValueError("Invalid value for `is_comment_count_visible`, must not be `None`")  # noqa: E501

        self._is_comment_count_visible = is_comment_count_visible

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
        if issubclass(BlockReactions, dict):
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
        if not isinstance(other, BlockReactions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
