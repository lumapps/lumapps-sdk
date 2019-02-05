Media Files and Library
=======================

The SDK includes a helper to easily manipulate the media files.

List media files in the library of a LumApps platform
-----------------------------------------------------

List the media for a specific language.

.. code-block:: python

    from lumapps.helpers.media import list_medias

    api = ... # previously obtained
    medias = list_medias(api, 'en')

Save one or multiple media files in the library of a LumApps site
-----------------------------------------------------------------

Uploading files in the media library of a given LumApps site is straightforward:
provide the instance id of the site, the files paths, and optionally the
languages and names for each file.

.. code-block:: python

    from lumapps.helpers.media import upload_and_save

    api = ... # previously obtained
    instance = ... # The instance id of your LumApps site
    files = ['path_to_file1', 'path_to_file2', ...]
    langs = ['en', 'fr', ...]
    names = ['file_1', 'file_2', ...]

    upload_and_save(api, instance, files, langs, names)

