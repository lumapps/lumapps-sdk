Users
=====

The SDK includes allows you to easily manipulate the users.

To list all users on your LumApps platform
--------------------------------------------

.. code-block:: python


    api = ... # previously obtained
    users = api.get_call("user", "list")

    for user in users:
        print("User {} [{}]".format(user.get("fullName"), user.get("uid")))

To create a user
----------------

Save a user by provinding an `email`, a `first_name` and a `last_name`.

.. code-block:: python

    api = ... # previously obtained
    user = {
        "email": "<email@mail.com>",
        "firstName": "<first_name>",
        "lastName": "<last_name>"
    }
    saved_user = api.get_call("user", "save", body=user)
    print(saved_user)

