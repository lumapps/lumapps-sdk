from typing import Any, Dict, Optional, Union

import httpx

from lumapps.api.client import ApiClient
from lumapps.api.errors import ApiClientError


def create_new_media(
    client: ApiClient,
    file_data_or_path: Union[bytes, str],
    doc_path: str,
    filename: str,
    mimetype: str,
    is_shared: bool,
    lang: Optional[str] = "en",
) -> Optional[Dict[str, Any]]:
    """ Upload a file and create a new media in LumApps media library.

        Args:
            client: The ApiClient used to make httpx to the LumApps Api.
            file_data_or_path: The filepath (str) or the data (bytes) to upload.
            doc_path: The doc path of the media to upload, this will decide where the media will go in your media library
                            (eg: provider=`<`my_provider`>`/site=`<`my_site_id`>`/resource=`<`my_parent_folder_id`>`)
            filename: The name of the file to upload. Once uploaded the file will appear with that name.
            mimetype: The mimeType fo the file to upload.
            is_shared: Wether the file is shared or not. Non shared files will only be visible by you.
            lang: The lang of the file to upload (default: "en").

        Raises:
            Exception: The data or file path type provided is not supported.

        Returns:
            Return the uploaded media if successfull, None otherwise.
    """

    if isinstance(file_data_or_path, str):
        file_data = open(file_data_or_path, "rb")
    elif isinstance(file_data_or_path, bytes):
        file_data = file_data_or_path
    else:
        raise ApiClientError(
            "File data or path type not supported: {}".format(type(file_data_or_path))
        )

    # Get upload url for the document
    body = {
        "fileName": filename,
        "lang": lang,
        "parentPath": doc_path,
        "shared": is_shared,
        "success": "/upload",
    }
    upload_infos = client.get_call("document/uploadUrl/get", body=body)
    upload_url = upload_infos["uploadUrl"]

    # Upload
    files_tuple_list = [("files", (filename, file_data, mimetype))]
    response = httpx.post(
        upload_url,
        headers={"Authorization": "Bearer " + client.token},
        files=files_tuple_list,
    )
    doc = response.json().get("items")

    if doc:
        return doc[0]
    return None


def add_media_file_for_lang(
    client: ApiClient,
    media: Dict[str, Any],
    file_data_or_path: str,
    filename: str,
    mimetype: str,
    lang: Optional[str] = "en",
    croppedContent: Optional[bool] = False,
) -> Optional[Dict[str, Any]]:
    """ Add a file to an existing LumApps media.

        Args:
            client: The ApiClient used to make httpx to the LumApps Api.
            media: The LumApps media on which the files have to be uploaded.
            file_data_or_path (Union[bytes, str]): The filepath (str) or the data (bytes) to upload.
            doc_path: The doc path of the media to upload, this will decide where the media will go in your media library
                            (eg: provider=`<`my_provider`>`/site=`<`my_site_id`>`/resource=`<`my_parent_folder_id`>`)
            filename: The name of the file to upload. Once uploaded the file will appear with that name.
            mimetype: The mimeType fo the file to upload.
            lang: The lang of the file to upload (default: "en").
            croppedContent (bool): Wether to add the file to the croppedContent instead or content (default: False)

        Returns:
            The updated media if succesfull, otherwise None.
    """

    # upload the file
    uploaded_file = _upload_new_media_file_of_given_lang(
        api=client,
        file_data_or_path=file_data_or_path,
        filename=filename,
        mimetype=mimetype,
        lang=lang,
    )
    if not uploaded_file:
        return media

    # update the media
    where = "croppedContent" if croppedContent else "content"
    media[where].append(uploaded_file)
    saved = client.get_call("document/update", body=media)
    return saved


def _upload_new_media_file_of_given_lang(
    client: ApiClient,
    file_data_or_path: Union[bytes, str],
    filename: str,
    mimetype: str,
    lang: Optional[str] = "en",
    prepare_for_lumapps: Optional[bool] = False,
):
    """ Upload a file to lumapps without creating an associated media

        Args:
            client: The ApiClient used to make httpx to the LumApps Api.
            file_data_or_path: The filepath or the data to upload.
            doc_path: The doc path of the media to upload, this will decide where the media will go in your media library
                            (eg: provider=`<`my_provider`>`/site=`<`my_site_id`>`/resource=`<`my_parent_folder_id`>`)
            filename: The name of the file to upload. Once uploaded the file will appear with that name.
            mimetype: The mimeType fo the file to upload.
            lang: The lang of the file to upload (default: "en").
            prepare_for_lumapps: prepare the return uploaded file to be usable as a lumapps media object (default: False)

        Raises:
            Exception: The data or file path type provided is not supported.

        Returns:
            Return the uploaded file if successfull, None otherwise.
        
        Notes:
            This is intended to be used to add new lang version/croppedContent to
            a LumApps media.
    """

    if isinstance(file_data_or_path, str):
        file_data = open(file_data_or_path, "rb")
    elif isinstance(file_data_or_path, bytes):
        file_data = file_data_or_path
    else:
        raise ApiClientError(
            "File data or path type not supported: {}".format(type(file_data_or_path))
        )

    # Get an upload url for the file
    response = httpx.get(
        "{}/upload?success=/upload".format(client.base_url),
        headers={"Authorization": "Bearer " + client.token},
    )
    upload_url = response.json().get("uploadUrl")

    if not upload_url:
        return

    # Upload the file
    response = httpx.post(
        upload_url,
        headers={"Authorization": "Bearer " + client.token},
        files={"upload-file": (filename, file_data, mimetype)},
    )
    uploaded_file = response.json()

    if not uploaded_file:
        return

    if prepare_for_lumapps:
        # Transform uploaded file to be accepted as a file in a media
        uploaded_file["lang"] = lang
        uploaded_file["value"] = uploaded_file["blobKey"]
        uploaded_file["servingUrl"] = uploaded_file["url"]
        uploaded_file["downloadUrl"] = uploaded_file["url"]
        del uploaded_file["blobKey"]
        del uploaded_file["upload"]
        del uploaded_file["filelink"]

    return uploaded_file
