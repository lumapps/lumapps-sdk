Users
=====

The SDK includes a helper to easily manipulate the users.

To list all users of your Lumapps plateform
------------------------------------------------

.. code-block:: python 

    from lumapps_api_sdk import user

    api = ... # previously obtained
    users = user.list(api)

    for usr_dict, usr_obj in users:
        print(usr_obj.uid)

To create a user
----------------

Save a user by provinding an `email`, a `first_name` and a `last_name`.

.. code-block:: python

    from lumapps_api_sdk.user import User

    api = ... # previously obtained
    usr = User(
          api,
          email="email",
          representation ={"firstName":"first_name","lastName":"last_name"},
    )
    success, errors = usr.save()
    print(success)


Groups
======

Groups in LumApps are named ``Feeds`` in the api and object definition. The SDK includes a helper to easily manipulate the groups.

To list all the feeds of your Lumapps plateform
-----------------------------------------------

.. code-block:: python

    from lumapps_api_sdk import group

    api = ... # previously obtained
    groups = group.list(api)

    for grp in groups:
        print(grp)

You can also filter by instance

.. code-block:: python

    groups = group.list(api, instance="my_instance")

To create a group synced to a google group email
------------------------------------------------

Save a feed by providing the `instance_id`, a `group_name`, a `google_group_email` and a `feed_type_id`.

.. code-block:: python

    from lumapps_api_helpers.group import Group

    api = ... # previously obtained
    group = Group(
        api,
        instance="instance_id",
        name="group_name",
        group="google_group_email",
        feed_type="feed_type_id",
    )
    success, errors = group.save()
    print(success)