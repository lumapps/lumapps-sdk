====================================
Getting Started with the Lumapps SDK
====================================

This quick guide will help you startup your first project using the Lumapps SDK

------------
Installation
------------

Install via ``pip``
-------------------

.. code-block:: bash

    $ pip install git+https://github.com/lumapps/lumapps-sdk.git

Install as a developer
----------------------

.. code-block:: bash

    $ git clone https://github.com/lumapps/lumapps-sdk.git
    $ cd lumapps-sdk
    $ pip install -e .
    $ pip install -r requirements_dev.txt


-----------------------------------
Authentication using a bearer token
-----------------------------------

Lumapps supports multiple ways of authentification. They are explained [here]() The fastest one to implement is the following:

You can obtain your token by logging to your Lumapps account. Go to https://sites.lumapps.com and authentificate. Once connected, open the javascript console of your browser and run:

.. code-block:: javascript

    var instance = window.location.pathname.split('/');
    instance = instance[instance.length-2];
    fetch(window.location.origin+"/service/init?customerHost="+window.location.host+"&instanceSlug="+instance+"&slug=").then(data=>{return data.json()}).then(res => {console.log(res.token)})


This will generate your personal Lumapps token that will be active for 60 minutes, and that we will use in the following steps

.. code-block:: python

    from lumapps_api_client.lib import ApiClient

    token = "[MY TOKEN]"
    api = ApiClient(token=token)

-------------------
Your first API call
-------------------

We will display the full name of a registered user in lumapps

.. code-block:: python

    user_email = "[A LUMAPPS USER EMAIL]"
    usr = api.get_call("user", "get", email=user_email)
    print("Hello {}".format(usr.get("fullName", "")))


---------
Some tips
---------

If you want to rapidly get info on your lumapps site you can use the ``?`` (``shift``+ ``,``), that shortcut will
display you infos on the current site you are connected on.