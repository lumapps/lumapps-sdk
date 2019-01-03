import logging

from lumapps_api_helpers.exceptions import (
    NotAuthorizedException,
    BadRequestException,
    NotFoundException,
)
from googleapiclient.errors import HttpError


def authorization_decorator(func):
    def func_wrapper(api, group, **kwargs):
        # type: (ApiClient, Group, dict) -> Union[boolean, dict]
        """Instantiate an empty group

        Args:
            api: the ApiClient instance to use for requests
            group: the Group instance to process
        """
        group_customer = group.get_attribute("customer")

        if group_customer == "":
            raise NotAuthorizedException("group requires a customer value")

        elif group_customer != api.customer:
            raise NotAuthorizedException(
                "group customer {} is not authorized for the user {}".format(
                    group_customer, api.email
                )
            )
        return func(api, group, **kwargs)

    return func_wrapper


class Group(object):
    """Lumapps feed object
    """

    def __init__(
        self,
        api,
        customer="",
        instance="",
        name="",
        uid="",
        remote_group="",
        feed_type="",
        representation=None,
    ):
        # type: (ApiClient, str, str, str, str, str, str, dict) -> None
        """Instantiate an empty group

        Args:
            api (object): the ApiClient instance to use for requests
            customer (str): the customer id of the group, used for autorization
            instance (str): the instance id, if not defined the group is a customer group (platform level)
            name (str): the group name
            uid (str): the lumapps unique id of the group, generated automatically at the first save
            remote_group (str): the remote email of the group (google group email for instance)
            type (str): feed type id
            representation (dict): a dictionary of all group attributes from lumapps
        """

        self._customer = customer if customer else api.customer
        self._uid = uid
        self._name = name
        self._instance = instance
        self._id = uid
        self._api = api
        self._remote_group = remote_group
        self._type = {"uid": feed_type}

        if representation is not None:
            self._set_representation(representation)

    def get_attribute(self, attr):
        # type: (str) -> Union[object, str, int]
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
        # type: (str, Union[str, int, object], str) -> None
        """

        Args:
            attr: feed attribute key to save
            value: feed attribute value to save
        """

        authorized_update_fields = (
            "customer",
            "status",
            "group",
            "synchronized",
            "instance",
            "name",
            "uid",
        )  # ("firstname","properties","lastname","fullname")
        label = "_{}".format(attr)

        if force or attr in authorized_update_fields:
            setattr(self, label, value)
        else:
            BadRequestException("attribute {} is not writable", attr)

    def _set_representation(self, result, force=True):
        # type: (dict, bool) -> None
        """Update the attribute of the class from a Lumapps Feed resource: https://api.lumapps.com/docs/output/_schemas/feed

        Args:
            result: Lumapps Feed resource
            force: whether or no to override writable fields protection
        """
        for k, v in iter(result.items()):
            self.set_attribute(k, v, force)

    def to_lumapps(self):
        # we only keep attributes starting with "_" and we strip the "_"
        ignore_fields = ["api", "type"]
        group = dict(
            (k[1:], v)
            for k, v in iter(vars(self).items())
            if k[0] == "_" and k[1:] not in ignore_fields
        )
        if self._type:
            group["type"] = self._type.get("uid")
        return group

    def set_type_by_label(self, label):
        types = get_types_by_label(self._api, self, label)

        if not types:
            raise NotFoundException("No group type found with that name or id")
        if len(types) > 1:
            raise BadRequestException("Multiple group types found with that name or id")

        self._type = types[0]

        return types[0]

    @property
    def uid(self):
        return str(self._uid)

    @property
    def name(self):
        return str(self._name)

    @property
    def type(self):
        return str(self._type)

    @property
    def api(self):
        return self._api

    def save(self, refresh_from_remote=False):

        try:
            result = save(self._api, self)

            if result:
                logging.info("saved group uid %s", result.get("uid"))
        except BadRequestException as e:
            return None, e

        if result is None:
            raise BadRequestException("Group has not been saved correctly")

        if result and refresh_from_remote:
            self._set_representation(result, True)

        return True, None

    def delete(self):
        # type () -> None

        try:
            delete(self.api, self)
        except BadRequestException as e:
            return None, e

        return True, None

    @staticmethod
    def new(
        api,
        customer="",
        instance="",
        name="",
        uid="",
        representation=None,
        fetch_by_name=False,
        fetch_by_id=False,
    ):
        if fetch_by_name:
            if name.isdigit():
                grp = get_by_uid(api, uid)
                logging.info("fetching groups by uid %s: %s", name, grp)
            if not grp:
                grps = get_by_name(api, name, instance)
                logging.info("fetching groups by name %s: %s", name, grps)
                if len(grps) == 1:
                    grp = grps[0]
                else:
                    raise BadRequestException("MULTIPLE_GRP_SAME_NAME")

            if grp:
                logging.info("group representation %s", grp)
                return Group(api=api, representation=grp)

        elif fetch_by_id:
            grp = get_by_uid(api, uid)
            if grp:
                return Group(api=api, representation=grp)

        return Group(
            api=api,
            instance=instance,
            customer=customer,
            name=name,
            uid=uid,
            representation=representation,
        )


@authorization_decorator
def save(api, group):
    # type (ApiClient, Group) -> Dict
    """Save or update a group (= Feed in Lumapps wording)

    Args:
        api: the ApiClient instance to use for requests
        group: the group to save, requires at least a customer and name values

    Returns:
        Lumapps Feed resource
    """
    if not group.name and not group.uid:
        raise BadRequestException("Group requires a field name or field uid")

    if not group.type:
        raise BadRequestException("Group requires a type id")

    try:
        grp = group.to_lumapps()
        print(grp)
        logging.info("saving group to remote %s ", grp)
        saved_grp = api.get_call("feed", "save", body=grp)

        return saved_grp

    except HttpError as e:
        raise BadRequestException(
            "Error {} Group {} has not been saved correctly.".format(str(e), group)
        )


@authorization_decorator
def delete(api, group):
    # type (ApiClient, Group) -> bool
    """Delete a group by uid

    Args:
        api (str): the ApiClient instance to use for requests
        group: the group to save, requires at least a customer and uuid values

    Returns:
        whether the operation succeeded
    """

    if group.uid is None or group.uid == "":
        raise BadRequestException("Group requires a field uid to delete")

    return api.get_call("feed", "delete", uid=group.uid) == ""


def get_types_by_label(api, group, label):
    types = api.get_call(
        "feedtype",
        "list",
        customer=api.customer,
        instance=group.get_attribute("instance"),
    )

    if types:
        filtered = [
            tp
            for tp in types
            if str(tp.get("uid")) == str(label) or str(tp.get("name")) == str(label)
        ]

        logging.info(
            "fetched types by label %s: %s filtered %s",
            label,
            len(types),
            len(filtered),
        )

        return filtered

    return None


def get_multi(api, uids):
    # type (ApiClient, list[str]) -> list[dict(str)]
    """A group by uid

    Args:
        api: the ApiClient instance to use for requests
        uids: list of uids to fetch

    Returns:
        list of Group elements
    """
    groups = api.get_call("feed", "getMulti", uid=uids)
    return groups


def get_by_name(api, name, instance=""):
    # type (ApiClient, str, str) -> dict(str)
    """A group by name

    Args:
        api: the ApiClient instance to use for requests
        name: name to search
        instance: the instance id

    Returns:
        a Lumapps Feed instance
    """
    logging.info("getting group by name %s", name)
    groups = list_sync(api, instance, query=name)
    return groups


def get_by_uid(api, uid):
    # type (ApiClient, str) -> dict(str)
    """A group by uid

    Args:
        api: the ApiClient instance to use for requests
        uid: uid to fetch

    Returns:
        a Lumapps Feed instance
    """
    logging.info("getting group by uid %s", uid)
    result = api.get_call("feed", "get", uid=uid)
    return result


def list_sync(api, instance="", fields="", **params):
    # type (ApiClient, str, str) -> list[dict[str]]
    """List all the groups of an instance. If no instance is provided , fetch the customer groups ( = platform feeds in lumapps)

    Args:
        api: the ApiClient instance to use for requests
        instance: the instance id
        fields: the fields to be returned
        ``**params``: optional  dictionary of search parameters as defined in https://api.lumapps.com/docs/feed/list

    Returns:
        list of Lumapps Feed resource
    """
    if not params:
        params = dict()
    if instance != "":
        params["instance"] = instance
    if fields != "":
        params["fields"] = fields

    if not params.get("body", None):
        params["body"] = {}

    result = api.get_call("feed", "search", **params)
    return result


def list_groups(api, instance="", fields="", **params):
    # type (ApiClient, str, str) -> list[dict[str]]
    """List all the groups of an instance. If no instance is provided , fetch the customer groups ( = platform feeds in lumapps)

    Args:
        api: the ApiClient instance to use for requests
        instance: the instance id
        fields: the fields to be returned
        ``**params``: optional  dictionary of search parameters as defined in https://api.lumapps.com/docs/feed/list

    Yields:
        a Lumapps Feed resource
    """
    if not params:
        params = dict()
    if instance != "":
        params["instance"] = instance
    if fields != "":
        params["fields"] = fields

    if not params.get("body", None):
        params["body"] = {}

    return api.iter_call("feed", "search", **params)


def update_users(group, users_to_add=list, users_to_remove=list):
    # TODO: Iterables and not lists
    # type (Group, list[User], list[User]) -> bool
    """Update the users of a group

    Args:
        group: the group to update
        users_to_add: list of users to add to the group
        users_to_remove: list of users to remove from the group

    Returns:
        whether the operation succeeded
    """
    api = group.api

    body = {
        "feed": group.uid,
        "addedUsers": [user.email for user in users_to_add],
        "removedUsers": [user.uid for user in users_to_remove],
    }
    logging.info(
        "updating users add:%s, remove:%s to remote groups %s ",
        body["addedUsers"],
        body["removedUsers"],
        body["feed"],
    )

    try:
        result = api.get_call("feed", "subscribers", "save", body=body)
    except HttpError as e:
        raise BadRequestException(
            "Error {} Group {} has not been saved correctly.".format(str(e), group)
        )

    return result == ""


def build_batch(api, groups):
    # type: (ApiClient, Iterator[dict[str]]) -> User
    """A generator for User instances from raw Lumapps user Iterator

    Args:
        api: the ApiClient instance to use for requests
        groups: list of dictionary

    Yields:
        a User attribute

    """
    logging.info("building batch %s", groups)
    for g in groups:
        group = Group.new(api, representation=g)
        yield g, group


def list_types_sync(api, instance="", **params):
    # type (ApiClient, str) -> list[dict[str]]
    """List all the groups types of an instance. If no instance is provided , fetch the platform types

    Args:
        api: the ApiClient instance to use for requests
        instance: the instance id
        ``**params``: optional  dictionary of search parameters as defined in https://api.lumapps.com/docs/feedtype/list

    Returns:
        list of Lumapps Feed resourcess
    """
    if not params:
        params = dict()
    if instance != "":
        params["instance"] = instance

    result = api.get_call("feedtype", "list", **params)
    return result
