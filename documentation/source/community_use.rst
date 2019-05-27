Contents
========

Create, retrieve and update contents.

List communities
----------------

.. code-block:: python

    contents = api.get_call(
        "community",
        "list",
        body={"lang":"en"}
    )

Get one community
---------------

.. code-block:: python

    content = api.get_call("community", "get", uid=2386179638984704)

Create a community
----------------

.. code-block:: python

    community = deepcopy(comunity_template)
    community.pop("uid")
    community.pop("id")
    community.pop("author", None)
    community.pop("authorId", None)
    community.pop("createdAt", None)
    community.pop("updatedAt", None)
    community.pop("updatedById", None)
    community.pop("name", None)
    community["title"] = {"en": name}
    community["slug"] = {"en": slug}
    community["customer"] = community.pop('customerId')
    community["instance"] = community.pop('instanceId')
    for templ in community["templates"]:
        if templ["functionalInnerId"] == "posts":
            community["template"] = deepcopy(templ)
            break
    # ...... set more properties .......
    community_saved = api.get_call("community", "save", body=community)
