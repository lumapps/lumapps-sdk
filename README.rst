**Lumapps SDK**
===============

.. image:: https://circleci.com/gh/lumapps/lumapps-sdk.svg?style=svg
    :target: https://circleci.com/gh/lumapps/lumapps-sdk

.. image:: https://black.readthedocs.io/en/stable/_static/license.svg
    :target: https://github.com/lumapps/lumapps-sdk/blob/master/LICENSE.rst
    :alt: License: MIT

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black
    :alt: Black style


*Please be aware the this sdk is still in beta version (0.1) and is undergoing a fast paced evolution that may break change the behaviour of some helpers*

*Make sure of the version you are using (Git tags & releases)*

----

Lumapps SDK is a set of tools to manipulate the `Lumapps API <https://api.lumapps.com/docs/start>`_.

This includes: 

- a client that support all the routes of the API (located in folder lumapps_api_client)
- a set of helper classes to easily manipulate Lumapps elements as Python Objects and classes (folder lumapps_api_helpers)


Quick start
===========

Installation::
------------

    $ pip install git+https://github.com/lumapps/lumapps-sdk.git


Get your token
--------------

Lumapps supports multiple ways of authentification.
The fastest one to implement is the following:

Get your token by logging to your Lumapps account.
Go to `https://sites.lumapps.com <https://sites.lumapps.com>`_ and authentificate.
Once connected, open the javascript console of your browser and run:

.. code-block:: javascript

    var instance = window.location.pathname.split('/');
    instance = instance[instance.length-2];
    fetch(window.location.origin+"/service/init?customerHost="+window.location.host+"&instanceSlug="+instance+"&slug=").then(data=>{return data.json()}).then(res => {console.log(res.token)})
    

This will generate your personal Lumapps token that will be active for 60 minutes, and that we will use in the following steps

Authentificate
--------------

.. code-block:: python

    from lumapps_api_client.lib import ApiClient
    token = "MY TOKEN"
    api = ApiClient(token=token)

Your first API call
~~~~~~~~~~~~~~~~~~~

Let's display the full name of a registered user in lumapps

.. code-block:: python

    user_email = "YOUR EMAIL"
    usr = api.get_call("user", "get", email=user_email)
    print("Hello {}".format(usr.get("fullName", "")))
    


Documentation
=============

The SDK documentation is available `here <https://lumapps.github.io/lumapps-sdk>`_.

Code convention
---------------

Docstring in PEP 484 type annotations format adapted to python 2.7 using comments.

How to get help, contribute, or provide feedback
================================================

Please refer to our `contributing guidelines <https://lumapps.github.io/lumapps-sdk/contributing.html#contributing-to-code>`_.

Copyright and license
=====================

Lumapps SDK is licensed under A MIT license - see the `LICENSE.rst <LICENSE.RST>`_ file.