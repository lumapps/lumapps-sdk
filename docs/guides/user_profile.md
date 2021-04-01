# User profile

Profile fields are defined in a `User Directory Module` and populate through the user `customProfile` properties.

## Get user Directory configuration

If you have the user directory module `id` use a `content/get` call with this id.

Else, get a list of user directory modules on an instance.

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

# prepare the request parameters
body = {
    "instanceId": "xxx",
    "lang": "en", # adapt
    "type": ["user_directory"],
    "excludeType": ["community", "custom", "custom_list", "image_gallery", "menu", "news", "news_list", "page", "post"],
    "action": "CUSTOM_EDIT"}

# get user directory modules list
user_directories = client.get_call(
    "content", "list", body=body)
```

The ̀`user_directories` will be a list of user directory modules.

Each user directory module has :
- a `uid` = `id`, we will use it as USER_DIRECTORY_MODULE_ID)
- a list of custom profile fields define in `template.components` , each with an `uuid`.

```python
# example, this user directory module define 2 fields:
# - "Title"
# - "Phone Number"
{
    "title": {
        "en": "Users Directory"
    },
    "id": "6486401110769664",
    "uid": "6486401110769664",
    "instance": "6288388086038528",
    "customer": "4664706704080896",
    "isDefaultUserDirectory": false,
    "type": "user_directory",
    "status": "LIVE",
    "slug": {
        "en": "users-directory"
    },
    "template": {
        "components": [
            {
                "uuid": "be3363f3-4df8-4a93-b27c-9c8c69258801",
                "title": {
                    "en": "Title"
                },
                "type": "inputText",
                "properties": {
                    "index": 0,
                    "isBound": true,
                    "boundMap": {
                        "text": "organizations/title",
                        "name": "API_PROFILE_FIELD_TITLE"
                    },
                    "icon": "bank"
                },
                "status": "LIVE",
            },
            {
                "uuid": "b72127e4-867a-4aba-a843-70c11dc599ef",
                "title": {
                    "fr": "Phone Number"
                },
                "type": "inputText",
                "properties": {
                    "editFeeds": [],
                    "availableValues": [
                        {}
                    ],
                    "icon": "account"
                },
                "status": "LIVE",
            }
        ],
        "heritable": false,
        "createdAt": "2018-04-12T07:43:23.624150",
        "uid": ""
    }
}
```


## Update the user profile

To update the user profile:
- get the user details for the corresponding user directory
- update or add value for the custom fields defined by the `user directory` module.
- save

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

CUSTOMER_ID = 'XXX'
INSTANCE_ID = 'YYY'

USER_DIRECTORY_MODULE_ID = '6486401110769664'
USER_TO_UPDATE_EMAIL = 'me@customer.com'

# get user details corresponding to a user directory module
user_to_update = client.get_call(
    'user', 'directory', 'get',
    email=USER_TO_UPDATE_EMAIL,
    contentId=USER_DIRECTORY_MODULE_ID)

# keep all user_to_update properties

# NB : if `user_to_update` doesn't have the `customProfile` property, add it
if "customProfile" not in userToUpadte:
    user_to_update['customProfile'] = {}

# Update the value of "Title" (get uid from user directory module definition).
field1uid = 'be3363f3-4df8-4a93-b27c-9c8c69258801'
user_to_update['customProfile'][field1uid] = 'Support Leader'

# Update the value of "Mobile" (get uid from user directory module definition).
field2uid = 'b72127e4-867a-4aba-a843-70c11dc599ef'
user_to_update['customProfile'][field2uid] = '00 11 22 33 44 55 66'

# /!\ To save a user in a user directory
# /!\ you must add the user directory module id in the user object like this:
user_to_update['contentId'] = USER_DIRECTORY_MODULE_ID

response = client.get_call(
    'user', 'directory', 'save',
    body=user_to_update)
```

```python

# to get more users at once
# use `POST user/directory/list body={'contentId':USER_DIRECTORY_MODULE_ID }`

users_to_update_list = client.get_call(
    'user', 'directory', 'list',
    contentId=USER_DIRECTORY_MODULE_ID )

```

Warning:

- if the field is defined with a bound value (ex for the "Title" above: 'organizations/title' ) the Title value will be store on the user under `apiProfile.organization.title`
- else, the value will be store under `customProfile.{fielduid}`.

```python
# example: the response of the previous call

{
    [...]
    "email": "me@customer.com",
    "customProfile" : {
        "b72127e4-867a-4aba-a843-70c11dc599ef": "00 11 22 33 44 55 66"
    }
    [...],
    "apiProfile": {
        "organization": {
            "title": "Support Leader"
        }
    }
}
```



