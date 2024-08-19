# Content


## Content listing
The `lang` parameter is mandatory for this call.

You can add more filters, see [apidoc](https://api.lumapps.com/docs/output/_schemas/servercontentcontentmessagescontentlistrequest)

```python
contents = client.get_call("content/list", body={"lang":"en"})
```

## Content details

This call is designed for content view

```python
content = client.get_call("content/get", uid="5386179638984704")
```

NB: `content.uid` = `content.id`

## Content update

Get content with `action=PAGE_EDIT` to have all the relevant data.

```python
content = client.get_call("content/get", uid="5386179638984704", action="PAGE_EDIT")
```

Note: the version number is used to lock the resource. You have to put the last version number of a content in `version` to be allowed to update a content, else a bad request: "CONTENT_NOT_UP_TO_DATE" will be returned.

# Content creation


The simplest way to create content is to use an existing template. This template will define all design configurations.

```python

base_template = api.get_call("template/get", uid="123456789")
# note : it's possible to use a content as well.

new_content = {
    "type": "page", # fixed
    "template": base_template[template], # copy all the structure (see below for details)
    "customContentType": base_template["customContentType"], # custom content type id
    "customer": base_template["customer"], # customer id
    "instance": base_template["instance"], # instance id
    "feedKeys": base_template["feedKeys"], # it's the `visibleBy` field in the front interface.
    "publicationDate": base_template[publicationDate],
    "title": {"en": "created content from api"},
    "slug": {"en": "create-content-from-api"}, # WARNING : should be unique per instance
    "metadata": [], # if any, provide metadata value uid
}

new_content_saved = client.get_call("content/save", body=new_content)

```

To create content on behalf of other users you have to be connected with this user.


---
# Objects explanation

## Content

```python
{
    "id" :"134567",
    "type":  "page",
    "status": "LIVE|ARCHIVED",
    "canonicalUrl": "https://...",
    "thumbnail" : "media library url",
    "publicationDate" : "2018-06-29T09:28:34.346124",
    "updatedAt": "2018-06-29T09:28:34.346124",
    "authorId": "23142536879786754" # set at creation time with the connected user
}
```

## Content.canonicalUrl

The `canonicalUrl` property contains the links that can be used to access the content.

## Content.template

The `template` property contains the whole page structure.

Widgets are directly placed in this structure.

```json
{ "template": {
    "components": [
        {
            "type": "row",
            "cells": [
            {
                "type": "cell",
                "components":[
                {
                    "type": "row|widget",
                    ...
                },
                ...]
            },
            ...]
        },
        ...]
    }
}
```
You should iterate over all the structure to find the correct widget to update.

## Content.thumbnail

A content can have a thumbnail, it's a picture associated with it and shows when listed in a content-list widget for instance.

When adding a thumbnail to a content you need to provide the blob key of the uploaded image in the `thumbnail` attribute. To upload and obtain that blobkey [see here](media.md).


### Update an existing thumbnail

```python
# First get the content
content = api.get_call('content/get', uid="6448894901878784")

# Update the thumbnail field by the media blob key
new_content = {
  ...
  "thumbnail": <your_new_blob_key>
}

# Resave the content
client.get_call('content/save', body=new_content)
```

## Widget

Widgets are placed in the `content.template` tree.

Widgets can be identified by their UUID

```json
{
    "type": "widget",
    "widgetType": "contact|html|...",
    "uuid": "ca2bd99c-7b7e-11e8-8255-abba20e0e453",
}
```

Specific configurations are in `properties`.

Ex for an HTML widget:
```json
{
    "type": "widget",
    "widgetType": "html",
    "uuid": "ca2bd99c-...",
    "properties": {
        "content":
            {
            "fr": "<p>Contenu html en français</p>",
            "en": "<p>Html text in english </p>"
            },
        "id": "identifier set in front > style > advance",
        "class": "class set in front > style > advance",
    }
}
```

The `properties>id` (or class) could be used to simplify widget access from code and communication with the design team.

**Working on widgets more easily**

To help you work on widget some helpers are available in the lumapps sdk

```python
from lumapps.api.helpers import widgets as widgets_helper

content = client.get_call("content/get") # get the lumapps content

# return the first found widget with the property widgetType equal to video
video_widget = widgets_helper.find_widget(content, widgetType="video")

# return all widgets with the property widgetType equal to video
all_video_widgets = widgets_helper.find_all_widgets(content, widgetType="video")

# return the first found widgetwith the property uuid equal test
widget_with_uuid_test = widgets_helper.find_widget(content, uuid="test")
```

See [Widgets](https://github.com/lumapps/lumapps-sdk/wiki/Widgets) for specific configurations.

See [Global Widgets](https://github.com/lumapps/lumapps-sdk/wiki/Global-Widget) for widgets defined at the instance level.


