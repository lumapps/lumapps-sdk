import logging
from lumapps_api_client.lib import ApiClient
from lumapps_api_helpers.exceptions import NotAuthorizedException, BadRequestException
from googleapiclient.errors import HttpError


def authorization_decorator(func):
    def func_wrapper(api, user, **kwargs):
        # type: (ApiClient, User) -> boolean | dict
        """Instantiate an empty group

        Args:
            api: the ApiClient instance to use for requests
            user: theUser instance to process

        """
        customer = user.get_attribute("customer")

        if customer == "":
            raise NotAuthorizedException("user requires a customer value")

        elif customer != api.customer:
            raise NotAuthorizedException(
                "user customer {} is not authorized for the user {}".format(
                    customer, api.email
                )
            )

        return func(api, user, **kwargs)

    return func_wrapper


class User(object):
    """
    Lumapps user object
    """

    USERS = []  # type: list[User]

    STATUS = {"LIVE": "enabled", "DISABLE": "disabled"}
    STATUS_INV = {v: k for k, v in STATUS.iteritems()}

    def __init__(self, api, customer="", email="", uid="", representation=None):
        # type: (ApiClient, str, str, str, dict) -> None
        """
        instantiate a empty user
        """

        self._customer = customer if customer else api.customer
        self._uid = uid
        self._email = email

        # _groups elements are of the form status: [Group] where
        # status ="to_remove" if user removed from the group but not synced with remote,
        # status ="to_add" if user add to the group locally but not synced with remote,
        # status ="synced" if user added to the group both locally and in remote.

        self._groups = {"to_add": [], "to_remove": [], "synced": []}
        self._id = uid
        self._api = api

        # default attributes to be able to save the user
        self._accountType = "external"
        self._isHidden = False
        self._isSuperAdmin = False

        if representation is not None:
            self._set_representation(representation)

        # User.USERS.append(self)

    @property
    def uid(self):
        return str(self._uid)

    @property
    def email(self):
        return self._email

    def __str__(self):
        return str(self.to_lumapps_dict())

    def __eq__(self, other):
        return self.to_lumapps_dict() == other.to_lumapps_dict()

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
            attr (str,str): feed attribute key to save
            value (int): feed attribute value to save
            force (bool): whether to force the storage of the attribute

        """
        if attr == "status":
            value = User.STATUS.get(value, value)

        if attr == "groups":
            if value and isinstance(value, str):
                return self.set_groups({"to_add": value.split(";")})

        label = "_{}".format(attr)

        authorized_update_fields = (
            "firstName",
            "properties",
            "lastName",
            "fullName",
            "status",
            "email",
            "subscriptions",
            "groups_label",
            "uid",
            "customProfile",
        )

        if force or attr in authorized_update_fields:
            setattr(self, label, value)
        else:
            BadRequestException("attribute {} is not writable", attr)

    def _set_representation(self, result, force=True):
        # type: (dict[str], boolean) -> None
        """
        Update the attribute of the class from a Lumapps User resource: https://api.lumapps.com/docs/output/_schemas/user

        Args:
            result (dict[str]): Lumapps User resource dictionnary
            force (boolean): save all the attributes from this dictionary

        """

        self._uid = result.get("uid")
        self._id = result.get("id")

        for k, v in result.iteritems():
            self.set_attribute(k, v, force)

    def get(self):
        # type: () -> object
        """fetch current user from lumapps using its email or uid
        """
        user = None
        result = get(self.api, self._email, self._uid)

        if result != None:
            if not self._customer or result.get("customer") == self._customer:
                logging.info("user %s found %s", self._email, result)
                self._set_representation(result, force=True)

            else:
                logging.warning(
                    "user %s found but doesn't belong to the customer %s",
                    self._email,
                    self._customer,
                )
                user = None

        return user

    def save(self, refresh_from_remote=False):

        try:
            result = save_or_update(self._api, self)
        except BadRequestException as e:
            return None, e

        if result is None:
            raise BadRequestException("User has not been saved correctly")

        else:
            self._set_representation(result)

        total_add = len(self._groups.get("to_add"))
        total_remove = len(self._groups.get("to_remove"))

        logging.info("updating user groups %s %s", total_add, total_remove)

        try:
            added, removed = self.update_remote_groups(
                self._groups.get("to_add"), self._groups.get("to_remove")
            )
        except BadRequestException as e:
            return None, e
        if len(added) != total_add or len(removed) != total_remove:
            raise BadRequestException("Some groups have not been updated correctly")

        if refresh_from_remote:
            self._set_representation(result, True)

        return True, None

    def get_groups(self, refresh=False, with_status=False):

        subscriptions = []

        if not refresh:
            if self._groups:
                if with_status:
                    return self._groups
                else:
                    return self._groups.get("synced")

            subscriptions = self.get_attribute("subscriptions", [])
            subscriptions = [sub.get("feed") for sub in subscriptions]

        if refresh or subscriptions == []:
            subscriptions = self.api.get_call(
                "user", "subscription", "list", userId=self._uid
            )
            if subscriptions:
                subscriptions = [sub.get("id") for sub in subscriptions]

        from group import get_multi

        groups = get_multi(subscriptions)
        self._groups = {"synced": groups}

        if with_status:
            return self._groups
        else:
            return groups

    def set_groups(self, groups, sync=False):
        from lumapps_api_sdk.group import Group

        if not groups:
            return

        to_add = [
            Group.new(
                api=self._api,
                customer=self._customer,
                name=grp,
                uid=grp,
                fetch_by_name=True,
            )
            for grp in groups.get("to_add", [])
        ]
        to_remove = [
            Group.new(
                api=self._api,
                customer=self._customer,
                name=grp,
                uid=grp,
                fetch_by_name=True,
            )
            for grp in groups.get("to_remove", [])
        ]

        self._groups["to_add"] = self._groups.get("to_add", []) + to_add
        self._groups["to_add"] = [
            grp for grp in self._groups.get("to_add", []) if grp not in to_remove
        ]

        self._groups["to_remove"] = self._groups.get("to_remove", []) + to_remove
        self._groups["to_remove"] = [
            grp for grp in self._groups.get("to_remove", []) if grp not in to_add
        ]

        if sync:
            self.update_remote_groups(
                self._groups.get("to_add", []), self._groups.get("to_remove", [])
            )

    def update_remote_groups(self, groups_to_add, groups_to_remove):
        from group import update_users

        added = []
        removed = []
        while len(groups_to_add):
            grp = groups_to_add.pop()
            success = update_users(grp, users_to_add=[self])
            if success:
                added.append(grp)

        for grp in groups_to_remove:
            success = update_users(grp, users_to_remove=[self])
            if success:
                removed.append(grp)

        return added, removed

    def to_lumapps_dict(self):
        # we only keep attributes starting with "_" and we strip the "_"

        ignore_fields = ["api", "groups", "subscriptions", "status"]

        user = dict(
            (k[1:], v)
            for k, v in vars(self).iteritems()
            if k[0] == "_" and k[1:] not in ignore_fields and v is not None
        )

        user["status"] = User.STATUS_INV.get(self._status, self._status)
        profile = self.get_attribute("customProfile")
        if profile:
            user.update(profile)
        return user

    @staticmethod
    def new(
        api,
        customer="",
        instance="",
        email="",
        uid="",
        representation=None,
        fetch_by_email=False,
        fetch_by_id=False,
    ):

        if fetch_by_email:
            usr = get_by_email(api, email)
            logging.info("fetching user by email %s: %s", email)
            if usr:
                return User(api=api, representation=usr[0])

        elif fetch_by_id:
            usr = get_by_uid(api, uid)
            if usr:
                return User(api=api, representation=usr[0])

        return User(
            api=api,
            customer=customer,
            email=email,
            uid=uid,
            representation=representation,
        )


def get(api, email="", uid="", fields=None):
    try:
        result = (
            api.get_call("user", "get", uid=uid, fields=fields)
            if uid
            else api.get_call("user", "get", email=email, fields=fields)
        )
        return result
    except Exception as e:
        logging.warning("user %s not found. Error %s", email, e.message)
        return None


@authorization_decorator
def save_or_update(api, user):
    # type: (ApiClient, User) ->  dict[str]
    """
    Args:
        api: the ApiClient instance to use for requests
        user: the user to save

    Returns:
        Saved user as Lumapps Resource or raise Exception if it fails
    """
    if not user.get_attribute("email"):
        raise BadRequestException("User requires an email")

    try:
        usr = user.to_lumapps_dict()
        logging.info("saving user to remote %s ", usr)
        saved_user = api.get_call("user", "save", body=usr)
        return saved_user

    except HttpError as e:
        raise BadRequestException(
            "Error {} User {} has not been saved correctly.".format(str(e), user)
        )


def deactivate(api, user):
    # type: (ApiClient) -> Iterator(User)
    """A generator for User instances from raw Lumapps user Iterator

    Args:
        api: the ApiClient instance to use for requests
        users: list of Lumapps User resource dictionnary

    Yields:
        a User attribute

    """
    user.set_attribute("status", User.STATUS.get("DISABLE"))
    return save_or_update(api, user)


def list_sync(api, **params):
    # type: (ApiClient) -> List(User)
    """Fetch users

    Args:
        api: the ApiClient instance to use for requests
        ``**params``: optional dictionary of search parameters as in https://api.lumapps.com/docs/user/list

    Returns:
        a User object

    """
    users = api.get_call("user", "list", **params)
    if users:
        return [user for user in build_batch(api, users)]


def list(api, **params):
    # type: (ApiClient) -> Iterator(User)
    """Fetch users

    Args:
        api: the ApiClient instance to use for requests
        ``**params``: optional dictionary of search parameters as in https://api.lumapps.com/docs/user/list

    Returns:
        a UserGenerator object

    """
    users_iter = api.iter_call("user", "list", **params)
    if users_iter:
        return build_batch(api, users_iter)


def build_batch(api, users):
    # type: (ApiClient, Iterator(dict[str])) -> User
    """A generator for User instances from raw Lumapps user Iterator

    Args:
        api: the ApiClient instance to use for requests
        users: list of Lumapps User dictionnary
        association: a dictionnary to translate the user dictionnary to User instance

    Yields:
        a User attribute

    """
    logging.info("building batch %s", users)
    for u in users:
        yield u, User.new(api, representation=u)


def get_by_email(api, email):
    # type (ApiClient, str, str) -> dict(str)
    """Get a user by email

    Args:
        api: the ApiClient instance to use for requests
        email: name to search
        instance: the instance id

    Returns:
        a Lumapps Feed instance
    """
    logging.info("getting user by email %s", email)
    result = api.get_call("user", "get", email=email)
    return result


def get_by_uid(api, uid):
    # type (ApiClient, str) -> dict(str)
    """Get a user by uid

    Args:
        api: the ApiClient instance to use for requests
        uid: uid to fetch

    Returns:
        a Lumapps Feed instance
    """
    logging.info("getting user by uid %s", uid)
    result = api.get_call("user", "get", uid=uid)
    return result
