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


class SiteReference(object):
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
    swagger_types = {"site_id": "str", "name": "str", "slug": "str"}

    attribute_map = {"site_id": "siteId", "name": "name", "slug": "slug"}

    def __init__(self, site_id=None, name=None, slug=None):  # noqa: E501
        """SiteReference - a model defined in Swagger"""  # noqa: E501
        self._site_id = None
        self._name = None
        self._slug = None
        self.discriminator = None
        self.site_id = site_id
        self.name = name
        self.slug = slug

    @property
    def site_id(self):
        """Gets the site_id of this SiteReference.  # noqa: E501

        The site's id.  # noqa: E501

        :return: The site_id of this SiteReference.  # noqa: E501
        :rtype: str
        """
        return self._site_id

    @site_id.setter
    def site_id(self, site_id):
        """Sets the site_id of this SiteReference.

        The site's id.  # noqa: E501

        :param site_id: The site_id of this SiteReference.  # noqa: E501
        :type: str
        """
        if site_id is None:
            raise ValueError(
                "Invalid value for `site_id`, must not be `None`"
            )  # noqa: E501

        self._site_id = site_id

    @property
    def name(self):
        """Gets the name of this SiteReference.  # noqa: E501

        The site's name.  # noqa: E501

        :return: The name of this SiteReference.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this SiteReference.

        The site's name.  # noqa: E501

        :param name: The name of this SiteReference.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError(
                "Invalid value for `name`, must not be `None`"
            )  # noqa: E501

        self._name = name

    @property
    def slug(self):
        """Gets the slug of this SiteReference.  # noqa: E501

        The site's slug.  # noqa: E501

        :return: The slug of this SiteReference.  # noqa: E501
        :rtype: str
        """
        return self._slug

    @slug.setter
    def slug(self, slug):
        """Sets the slug of this SiteReference.

        The site's slug.  # noqa: E501

        :param slug: The slug of this SiteReference.  # noqa: E501
        :type: str
        """
        if slug is None:
            raise ValueError(
                "Invalid value for `slug`, must not be `None`"
            )  # noqa: E501

        self._slug = slug

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
        if issubclass(SiteReference, dict):
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
        if not isinstance(other, SiteReference):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other