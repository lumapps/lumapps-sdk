Media Management
================

The SDK includes a helper to easily manipulate the medias.

List all the medias of your Lumapps platform
--------------------------------------------

You can list all the medias in a specific language with this helper.

.. code-block:: python

    from lumapps_api_helpers.media import list_medias

    api = ... # previously obtained
    medias = list_medias(api, 'en')

Save one or several media(s) to your Lumapps site
-------------------------------------------------

We provide you a simple way to upload one or several
media(s) at the same time to your Lumapps site (instance).
Just provide the instance id, the files paths and optionaly the langs and names
of each file and we upload and save it for you.

.. code-block:: python

    from lumapps_api_helpers.media import upload_and_save

    api = ... # previously obtained
    instance = ... # The instance id of your Lumapps site
    files = ['path_to_file1', 'path_to_file2', ...]
    langs = ['en', 'fr', ...]
    names = ['file_1', 'file_2', ...]

    upload_and_save(api, instance, files, langs, names)