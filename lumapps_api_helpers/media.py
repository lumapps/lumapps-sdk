import logging

def list_medias(api, lang, **params):
    # type (ApiClient, str, dict) -> (Iterable[dict])
    """List all the medias.

        Args:
            api (object): The ApiClient instance used for request.
            lang (str): the lang. Defaults to english (en).
            ``**params``: optional  dictionary of search parameters as defined in https://api.lumapps.com/docs/media/list.

        Yields:
            a Lumapps Media resource
    """
    params["lang"] = lang if lang else "en"
    return api.iter_call("media", "list", **params)


def upload_file(api, f):
    # type: (ApiClient, list[str]) -> (dict)
    """Upload a file to the googleusercontent of the ApiClient.

        Args:
            api (object): The ApiClient instance used for request.
            files (list[str]): A list of paths to the files to upload.
        
        Returns:
            list[dict]: The post request return.
    """
    upload_url = api.get_call("file", "uploadUrl")["uploadUrl"]
    response = api.get_authed_session().post(
        upload_url, files=[("files", open(f, "rb"))]
    )
    if response.status_code != 200:
        logging.error(
            "Upload file {} failed. Response content was {}.".format(f, response.content)
        )
        raise Exception(str(response.content))
    uploaded_file = response.json()
    return uploaded_file


def save_media(api, media):
    # type: (ApiClient, dict) -> None
    """Save a media.

        Args:
            api (object): The ApiClient instance used to request.
            media (dict): the media to save.

        Returns:
            dict: A dict that is the response of the save request. It contains all the info about the saved media.
    """
    return api.get_call("media", "save", body=media)


def uploaded_to_media(uploaded_file, instance, lang, name=None):
    # type: (dict, str, str, str) -> dict
    """Transform an uploaded file (post reponse) into a minimal media.

        Args:
            uploaded_file (dict): The post reponse returned after uploading a file.
            lang (str): the lang associated to the file.
            instance (str): the instance where the file will live (and be saved).
        
        Returns:
            dict: A media ressource as described in https://api.lumapps.com/docs/output/_schemas/media.
    """
    media = {}
    media["instance"] = instance
    media["content"] = [
        {
            "ext": uploaded_file.get("ext"),
            "height": uploaded_file.get("height", 0),
            "width": uploaded_file.get("width", 0),
            "lang": lang,
            "mimeType": uploaded_file.get("mimeType"),
            "name": name or uploaded_file.get("name"),
            "url": uploaded_file.get("url"),
            "servingUrl": uploaded_file.get("url"),
            "size": uploaded_file.get("fileSize"),
            "type": uploaded_file.get("type"),
            "value": uploaded_file.get("blobKey"),
        }
    ]
    media["name"] = {lang: name or uploaded_file.get("name")}
    return media


def upload_and_save(api, instance, files, langs=None, names=None):
    # type: (ApiClient, str, list[str], list[str], list[str]) -> None
    """Upload and save a list of 1 or several files to the specified lumapps site (instance).

        Args:
            api (object): The ApiClient instance used to request.
            instance (str): the instance where to save the files
            files (list[str]): A list of the paths to the files to save.
            langs (list[str], optional): A list containing the lang associated to each file. Defaults to english.
            name (list[str], optional): A list containing the name associated to each file. Defaults to the filename.
        
        Returns:
            list: A list containing the info on each saved media.
    """
    langs = ["en"] * len(files) if langs is None else langs
    names = [None] * len(files) if names is None else names
    saved_medias = []
    for f, lang, name in zip(files, langs, names):
        uploaded_file = upload_file(api, f)
        logging.info("File {} uploaded !")
        media = uploaded_to_media(uploaded_file, instance, lang, name)
        media_saved = save_media(api, media)
        if media_saved:
            saved_medias.append(media_saved)
            logging.info("File : {} saved !".format(f))
            print("File : {} saved !".format(f))
        print(media_saved)

    return saved_medias


# ------------------------------------------------------------------------------------#
#                                                                                    #
#                                   Media folders                                    #
#                                                                                    #
# ------------------------------------------------------------------------------------#


def list_media_folders(api, lang, **params):
    # type: (ApiClient, str, dict) -> Iterable[dict]
    """List all media folder associated to a lang in

        Args:
            api (object): The instance of the ApiClient used for request.
            lang (str): The lang associated to the folders.
            ``**params`` (dict, optional): A dict containing other optional parameters as described in https://api.lumapps.com/docs/media/folder/list

        Yields:
            A LumApps MediaFolder resource.
    """
    if not params:
        params = {}
    params["lang"] = lang
    return api.iter_call("media", "folder", "list", **params)


def create_media_folder(api, instance, lang, name, **params):
    # type: (ApiClient, str, str, str) -> dict
    """Create a media folder

        Args:
            api (object): The ApiClient instance used to requests.
            instance (str): The instance id of the Lumapps site.
            lang (str): The lang associated to the folder.
            name (str): The name of the folder.
            ``**params`` (dict): A dict of optionnal params as described in https://api.lumapps.com/docs/output/_schemas/folder

        Returns:
            dict: The repsonse of the post request, ie a folder object.
    """
    if not params:
        params = {}
    params["instance"] = instance
    params["name"] = {lang: name}
    response = api.get_call("media", "folder", "save", body=params)
    return response


def move_media_to_folder(api, itemid, folderid, **params):
    # type: (ApiClient, str, str, dict) -> dict
    """Move a media in a specified folder.

        Args:
            api (object): The ApiClient instance used for the request.
            itemid (str): The id of the media to move.
            folderid (str): The id of the folder to move the media into.
            ``**params`` (dict, optional): An optional dict of parameters as described in https://api.lumapps.com/docs/output/_schemas/servermediamediamessagesfilesystemitemmoverequest

        Returns:
            dict: The response of the post request containing the media object that was moved.
    """
    if not params:
        params = {}
    params["itemId"] = itemid
    params["destinationFolderId"] = folderid
    return api.get_call("media", "media", "move", body=params)
