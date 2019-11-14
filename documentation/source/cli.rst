==================
Client Application
==================

-------------------
Required parameters
-------------------

``--auth`` JSON file that contains auth information of a service account or web auth

* Service account (the file you download from GCP should do as-is)

  .. code-block:: json

      {
        "type": "service_account",
        "project_id": "gbl-imt-ve-lifepulse-dev",
        "private_key_id": "..."
      }

* Web auth

  .. code-block:: json

      {
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "client_id": "...",
        "client_secret": "...",
        "refresh_token": "..."
      }

* Bearer

  .. code-block:: json

      {
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "client_id": "...",
        "client_secret": "...",
        "refresh_token": "..."
      }

--------------
Usage examples
--------------

**List API methods**

.. code-block:: bash

    lac --auth web_auth.json

**List methods beginning with 'comm'**

.. code-block:: bash

    lac --auth web_auth.json comm

**Get list of 'instances'**

.. code-block:: bash

    lac --auth web_auth.json instance list

**Get arguments for 'template list'**

.. code-block:: bash

    lac --auth web_auth.json template list -h

**Get list of 'templates'**

.. code-block:: bash

    lac --auth web_auth.json template list instance=6724836101455872

**Get current user using Service Account with domain-wide delegation**

.. code-block:: bash

    lac --auth service_account.json --user john.doe@foobar.com user get

**Get current user using Service Account to get token from LumApps**

.. code-block:: bash

    lac --auth service_account.json --email john.doe@foobar.com user get
