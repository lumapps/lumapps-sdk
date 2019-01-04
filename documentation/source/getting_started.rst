====================================
Getting Started with the LumApps SDK
====================================

This quick guide will help you started with your first project using LumApps SDK

------------
Installation
------------

Install with ``pip``
--------------------

.. code-block:: bash

    $ pip install git+https://github.com/lumapps/lumapps-sdk.git

Install from sources
--------------------

.. code-block:: bash

    $ git clone https://github.com/lumapps/lumapps-sdk.git
    $ cd lumapps-sdk
    $ pip install -e .
    $ pip install -r requirements_dev.txt

-----------------------------------
Authentication using a bearer token
-----------------------------------

LumApps supports multiple methods of authentification. They are explained
[here](). The following method allows a LumApps user to use his or her
bearer token with LumApps SDK.

You can retrieve such a bearer token by logging in LumApps in your Chrome or
Firefox browser. Go to https://sites.lumapps.com and log in, if you are not
already. Then open the developer console of your browser and run the following
javascript in the Console tab:

.. code-block:: javascript

    var instance = window.location.pathname.split('/');
    instance = instance[instance.length-2];
    fetch(window.location.origin+"/service/init?customerHost="+window.location.host+"&instanceSlug="+instance+"&slug=").then(data=>{return data.json()}).then(res => {console.log(res.token)})

This will generate your personal LumApps token that will be valid for 60
minutes, and that we will use in the following steps.

.. code-block:: python

    from lumapps_api_client.lib import ApiClient
    token = "[MY TOKEN]"
    api = ApiClient(token=token)

-------------------
Your first API call
-------------------

Let's display the full name of a registered user in lumapps

.. code-block:: python

    user_email = "[A LUMAPPS USER EMAIL]"
    usr = api.get_call("user", "get", email=user_email)
    print("Hello {}".format(usr.get("fullName", "")))

---------
Some tips
---------

If you want to rapidly get info on your lumapps site you can use the ``?`` (``shift``+ ``,``), that shortcut will
display you infos on the current site you are connected on.