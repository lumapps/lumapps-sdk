# Media

## Uploading a media

### With the LumApps SDK

We provide a helper method to ease the process of uploading a media

```python
uploaded_media = client.upload_call("path_to_my_file")
```

### Manualy

To upload a media you will need to get an upload and then upload the media itself.

1. **Obtaining an upload url**

    To do that you'll need to call the `document/uploadUrl/get` endpoint (Make sure that you include you bearer token in the Authorization headers)

    Here is an example of the payload to send

    ```json
    {
        "fileName": "Screenshot_2020-04-16 Design System.png",
        "shared": true,
        "success": "/upload",
        "parentPath": "provider=local/site=5414442267049984",
    }
    ```
    The attributes are:

    * *FileName* : The name of the file has it will appear in the media library once uploaded
    * *shared* : Wether the file should be shared. If false the file will only be accessible to the user making the upload call (ie, the one authenticated by the token used in the call).
    * *success*: Leave it to success
    * *parentPath*: The path of where the media will be uploaded in the media library. If you want to upload in a specific folder, add `/resource=<folder_id>` at the end of path. See [media path](#Media-path) for more infos

    This will give you an **uploadUrl** to use next

2. **Uploading the media**

    Now that you have an **uploadUrl** you will use it to send you file in a POST request (Make sure that you include you bearer token in the Authorization headers). This request in a regular multipart upload,

    ```python
    response = self.client.post(
            upload_url, files={"upload-file": (name, file, mime_type)}
        )
    ```

    If all goes well you should have successfully uploaded you file to the media library


## Media path

In the LumApps library media are saved and retrieved via their path.

This path identifies where the media is situated either in the LumApps library itself, or in a gdrive or microsoft drive.

This path is of the form `provider=<provider>/site=<site_id>/resource=<resource_id>` and is called `docPath` or `parentPath` depending on the situation.

* The provider can be **local** (lumapps media library), **drive** (google drive).
* The `site_id` is the id of the LumApps site the media is on.
* The `resource_id` is the id of the media.

The path is named `docPath` when you for instance retrieve the media and it identifies the media and is named `parentPath` when for instance you ask for an upload url and it identified where to upload.

## Blob key

### Upload an image and obtain the blob key

First [upload your file](#Uploading-a-media)
Once uploaded the api return the uploaded media of the form

```json
{
    "uid": "5278825007677440",
    "isFolder": false,
    "customContentTypeKey": null,
    "updatedAt": "2020-06-25T08:31:50.737799",
    "isStarred": null,
    "id": "5278825007677440",
    "createdAt": "2020-06-25T08:31:50.751663",
    "content": [
        {
            "lang": "fr",
            "mimeType": "image/png",
            "uuid": "",
            "url": "https://sites.lumapps.com/serve/AMIfv95xFdNZT4x8ZCwYxVa4Ekr3hPU0ZRXJ_5na3mMJ_IwkfRW0-Vu-jY8DgPncGSq2UcAH-O_BnktwDOduHBccB8IgOCUQkoFv3WIzMH9FEOQVaX5uj7SA0BsdjPFdnqYKcOMRz4KPyBUPq66pXc3OpX3rycTxwQ/",
            "type": "image",
            "size": 46667,
            "servingUrl": "https://sites.lumapps.com/serve/AMIfv95xFdNZT4x8ZCwYxVa4Ekr3hPU0ZRXJ_5na3mMJ_IwkfRW0-Vu-jY8DgPncGSq2UcAH-O_BnktwDOduHBccB8IgOCUQkoFv3WIzMH9FEOQVaX5uj7SA0BsdjPFdnqYKcOMRz4KPyBUPq66pXc3OpX3rycTxwQ/",
            "value": "AMIfv95xFdNZT4x8ZCwYxVa4Ekr3hPU0ZRXJ_5na3mMJ_IwkfRW0-Vu-jY8DgPncGSq2UcAH-O_BnktwDOduHBccB8IgOCUQkoFv3WIzMH9FEOQVaX5uj7SA0BsdjPFdnqYKcOMRz4KPyBUPq66pXc3OpX3rycTxwQ",
            "height": 717,
            ....
        }
    ]
}
```

The blob key is the `value` property in content

### Obtain the blob key of an existing media

To obtain an existing blob key you have 2 main solutions

1. Get the media (`document/get` or `document/list`) via API's and extract the key. In that case the key should be in `content -> value`

2. Copy/paste it from the LumApps admin.

    For that go to the media library => find your media => click on the three dots => Obtain a link

    This should give you a link the image, the blob key is containned in that link, between two `/` and after `server/`

    (eg, https://sites.lumapps.com/serve/**AMIfv96jY01ZxeT4S-Yanb7h5SigIG-ZIVcYK1Th95Z2gOkJet6Trdl2hntG8C_**
    **x17K0wqFms2cLOCIYPSreUsDsTQPyjVVZGh-IOJxaxLmmz6IxnWw1W0HapKyrwAfJsmNQsLwg6wNnbOrLZdeJdsMgGt_GYiDSb0pr**
    **uLlkBn5toPLNK1Cd5gykYLu4UBEdgsvyksHOcwYxf6rUwSJGGD3vkL_C0tz_3If5vIPwo42nEAvIwU2Vx7WeI__cK9Tq2CooTSTn**
    **L37iMKBsPxuGNXYLVLEApbHGJBNtoKiT_tswmKsL8Ub3_TBrtSZIOhnjajucQCZDWDK0Gsx4R6K7zT7NcQtwA**/tricot2.jpg)