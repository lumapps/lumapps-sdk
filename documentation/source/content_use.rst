Content Management
==================

The SDK includes a helper to easily manipulate the content.

Content Listing
---------------

.. code-block:: python

    contents = api.get_call("content", "list", body={"lang":"en"})

Content details
---------------

.. code-block:: python

    content = api.get_call("content", "get",uid=5386179638984704)


Content creation
----------------

.. code-block:: python

    new_content = {"type": "page",
                "template": content[template], # from existing content or template
                "customContentType": content["customContentType"],
                "customer": content["customer"],
                "instance": content["instance"],
                "feedKeys": content["feedKeys"], 
                "publicationDate": content[publicationDate],
                "title": {"en": "created content from api"},
                "slug": {"en": "create-content-from-api"}, # WARNING : unique
                "metadata": [], # if any
            }

    new_content_saved = api.get_call("content","save",body=new_content)