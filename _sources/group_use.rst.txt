Groups
======

Groups in LumApps are named ``Feeds`` in the api and object definition. The SDK includes allows you to easily manipulate the groups.

To list all the feeds of your LumApps platform
-----------------------------------------------

.. code-block:: python

    api = ... # previously obtained
    groups = api.get_call("feed", "list")

    for grp in groups:
        print("Group {} []".format(grp.get("name"), grp.get("uid")))

You can also filter by instance

.. code-block:: python

    groups = api.get_call("feed", "list", instance="<my_instance>")

To create a group synced to a google group email
------------------------------------------------

Save a feed by providing the `instance_id`, a `group_name`, a `google_group_email` and a `feed_type_id`.

.. code-block:: python

    api = ... # previously obtained
    group = {
        instance="<instance_id>",
        name="<group_name>",
        group="<google_group_email>",
        feed_type="<group_type_id>"
    }

    saved_group = api.get_call("feed", "save", body=group)
    print(saved_group)