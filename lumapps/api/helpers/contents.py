from typing import Any, Dict, Optional

import httpx

from lumapps.api.base_client import BaseClient


def list_contents_by_type(
    client: BaseClient, lang: Optional[str] = "en", contenttype_list=[str],
) -> Optional[Dict[str, Any]]:
    """ Get a list of custom content types.

            Args:
                client: The BaseClient used to make httpx to the LumApps Api.
                lang: The lang of the file to upload (default: "en").

            Raises:
                Exception: 

            Returns:
                Return
        """  # noqa

    reponse = httpx.post(
        "content/list",
        headers={"Authorization": "Bearer " + client.token},
        data={"lang": lang, "customContentType": contenttype_list},
    )
    content_list = reponse.json().get("items")
    return content_list
