Contents
========

Create, retrieve and update contents.

List contents
-------------

.. code-block:: python

    contents = api.get_call("content", "list", body={"lang":"en"})

Get one content
---------------

.. code-block:: python

    content = api.get_call("content", "get",uid=5386179638984704)

Create a content
----------------

.. code-block:: python

    new_content = {
        "type": "page",
        "template": template, # from existing content or template
        "customContentType": "customContentType id",
        "customer": "customer id",
        "instance": "instance id",
        "feedKeys": ["feed id 1", ...],
        "publicationDate": "2000-01-01",
        "title": {"en": "created content from api"},
        "slug": {"en": "create-content-from-api"}, # WARNING: must be unique
        "metadata": [], # optional
    }

    new_content_saved = api.get_call("content", "save", body=new_content)