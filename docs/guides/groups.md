Group in LumApps are named `Feeds` in the api and object definition.

## List
Groups can be defined at platform or instance level.

Get the list of group
```python
client.get_call("feed/list") # platform and instances

client.get_call("feed/list", instance="1234") # one instance
```

Groups have a `type`, get details with
```python
client.get_call("feedtype/list") # platform only

client.get_call("feedtype/list", instance="12345") # one one instance
```


## Create a group

```python
from lumapps.api.client import ApiClient

client = ApiClient(token="<your_token>")

group = {
    "customer": "123456789",
    "name": "Display name",
    "functionalInnerId": "any, for external use only",
    "type": "12345678", # feed type
    }
}
new_group = client.get_call("feed/save", body=group)
```
## Update a group

```python
group = client.get_call("feed/get", uid=feedUid)

# change group name then save

group = client.get_call("feed/save", body=group)

```
## Delete a group

```python
# user feed/delete with the feed ui

client.get_call("feed/delete", uid=feedUid)
```
## Create a group synced with a existing google or microsoft group

You first need to know the identity provider configuration:

```python
idps = client.get_call("customer/identityprovider/list")

"""
{"items": [
    {
    "name": "customName",
    "domain": "mydomain.net",
    "id": "a913b61f-09ed-4e97-b3ec-cbbf714fe10e",
    "type": "google|microsoft|mail|okta",
    "customerKey": "123456789",
    "nbUsers": 42,
    ...
},
...
]}

"""
```
Then create a feed:

```python
feed = {
    "customer": "123456789",
    "name": "Display name",
    "groups": [
        {
        "identityProvider": "a913b61f-09ed-4e97-b3ec-cbbf714fe10e",
        "group": "the google email of the group",
        }
    ],
    "functionalInnerId": "any, for external use only",
    "type": "12345678", # feed type
    }
}
new_group = api.get_call('feed', 'save', body=group)
```

Notes:
- you can add one group per identity provider. If you try to add more than one group per idp, the last one will be preserved.
- the group email should exist, in the other case the api will return an error.
- only `google` and `microsoft` idp supports the group synchronization.
- members are retrieved asynchronously by the server, you may need to wait before doing a member list request to have the full list of members.

## List the members of one or many feed

use the user/list endpoint with the feed id in the `feeds` filter.

```python
feed_members = api.get_call('user', 'list', feeds=['1345'])

```
## update members of a group

```python
from lumapps.api.client import ApiClient

client = ApiClient(token="<your_token>")

body = {
    "feed": "1234",
    "addedUsers":
        [
            "user_email_to add",
            ...
        ],
    "removedUsers":
        [
            "user_email_to remove",
            ...
        ]}
}

client.get_call('feed', 'subscribers', 'save', body=body)
```




