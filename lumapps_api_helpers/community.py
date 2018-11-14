import logging

from lumapps_api_sdk.exceptions import BadRequestException
from lumapps_api_client.lib import ApiClient

from server.modules.sdk.user import User


class Community(object):
    """
    Lumapps community object
    """

    def __init__(
        self,
        api,
        customer="",
        instance="",
        title="",
        uid="",
        author="",
        representation=None,
    ):
        # type: (ApiClient, str, str, str, Community, dict) -> None
        """
        instantiate an empty community
        Args:
            api: the ApiClient instance to use for requests
            customer: the customer id of the community, used for autorization
            instance: the instance id, if not defined the community is a customer community (platform level)
            title: the community name
            author: Community object of the community owner
            uid: the lumapps unique id of the community, generated automatically at the first save
            representation: a dictionary of all community attributes from lumapps
        """

        self._customer = customer if customer else api.customer
        self._uid = uid
        self._title = title
        self._author = author
        self._instance = instance
        self._id = uid
        self._api = api

        if representation is not None:
            self._set_representation(representation)

    @property
    def uid(self):
        return str(self._uid)

    @property
    def title(self):
        return self._title

    @staticmethod
    def new(api, customer="", instance="", uid="", title="", representation=None):

        return Community(
            api=api,
            instance=instance,
            customer=customer,
            title=title,
            uid=uid,
            representation=representation,
        )

    def get_attribute(self, attr):
        # type: (str) -> object | str | int
        """

        Args:
            attr: the attribute to fetch
        Returns:
            the value of this attribute from the full dictionary of the group attributes
        """
        label = "_{}".format(attr)
        if hasattr(self, label):
            return getattr(self, label, "")

    def set_attribute(self, attr, value, force=False):
        # type: (str, str | int | object, boolean) -> None
        """

        Args:
            attr: feed attribute key to save
            value: feed attribute value to save
            force: whether to force the storage of the attribute
        Returns: None
        """

        if attr == "adminKeys":
            attr = "admins"
            value = [User.new(self.api, self._customer, uid=usr) for usr in value]

        if attr == "userKeys":
            attr = "users"
            value = [User.new(self.api, self._customer, uid=usr) for usr in value]

        if attr == "authorId":
            attr = "author"
            value = User.new(self.api, self._customer, uid=value)

        label = "_{}".format(attr)

        authorized_update_fields = (
            "admins",
            "users",
            "author",
            "title",
            "status",
            "instance",
            "type",
            "description",
        )

        if force or attr in authorized_update_fields:
            setattr(self, label, value)
        else:
            BadRequestException("attribute {} is not writable", attr)

    def _set_representation(self, result, force=False):
        # type: (dict[str], boolean) -> None
        """
        Update the attribute of the class from a Lumapps Community resource: https://api.lumapps.com/docs/output/_schemas/community

        Args:
            result: Lumapps Community resource dictionnary
            force: save all the attributes from this dictionary
        Returns: None
        """

        self._uid = result.get("uid")
        self._id = result.get("id")

        for k, v in result.iteritems():
            self.set_attribute(k, v, force)

    def to_lumapps_dict(self):
        # we only keep attributes starting with "_" and we strip the "_"

        ignore_fields = ["api", "author", "admins", "users"]

        community = dict(
            (k[1:], v)
            for k, v in vars(self).iteritems()
            if k[0] == "_" and k[1:] not in ignore_fields and v is not None
        )

        community["authorId"] = self._author.uid
        community["adminKeys"] = [usr.uid for usr in self._admins]
        community["userKeys"] = [usr.uid for usr in self._users]

        return community

    def get_posts(self, **params):
        # type: (ApiClient) -> Iterator(dict[str])
        """
        fetch community posts
        Arguments:
            **params: optional dictionary of search parameters as in https://api.lumapps.com/docs/output/_schemas/servercontentcommunitypostpostmessagespostlistrequest
        Return: a Community Post Generator object

        """
        params["contentId"] = self._uid
        params["instanceId"] = self._api.instanceId

        if not params.get("lang", None):
            params["lang"] = "en"

        if not params.get("fields", None):
            params[
                "fields"
            ] = "cursor,items(author,content,createdAt,uid,status,tags,title)"

        return self._api.iter_call("community", "post", "search", body=params)


def list(api, **params):
    # type: (ApiClient) -> Iterator(dict[str])
    """
    fetch communities
    Arguments:
        api: the ApiClient instance to use for requests
        **params: optional dictionary of search parameters as in https://api.lumapps.com/docs/community/list
    Return: a Community Generator object

    """

    if not params.get("fields", None):
        params[
            "fields"
        ] = "cursor,items(adminKeys,instance,status,title,type,uid,userKeys,authorId, description)"

    return api.iter_call("community", "list", **params)


def build_batch(api, communities, association=None):
    # type: (ApiClient, Iterator(dict[str]), dict[str]) -> Community
    """
    A generator for Community instances from raw Lumapps community Iterator
    Arguments:
        api: the ApiClient instance to use for requests
        communities: list of Lumapps Community dictionnary
        association: a dictionnary to translate the community dictionnary to Community instance
    Yields: a Community attribute

    """
    logging.info("building batch communities")
    for u in communities:
        if association:
            community = dict([(association.get(k, k), v) for (k, v) in u.iteritems()])
        else:
            community = u
            community = Community(api, representation=community)
        yield community


def list_sync(api, instance="", **params):
    # type (ApiClient, str) -> list[dict[str]]
    """
    list all the communities of an instance. If no instance is provided , all the communities

    Args:
        api: the ApiClient instance to use for requests
        instance: the instance id
        **params: optional  dictionary of search parameters as defined in https://api.lumapps.com/docs/community/list
    Returns: list of Lumapps Community resources
    """
    if not params:
        params = dict()
    if instance != "":
        params["instance"] = instance

    result = api.get_call("community", "list", **params)
    return result
