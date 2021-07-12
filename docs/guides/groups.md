Group in LumApps are named `Feeds` in the api and object definition.
Groups can be defined at platform or instance level.

## List groups

Get the list of group
```python
client.get_call("feed/list") # platform and instances

client.get_call("feed/list", instance="<your_instance>") # one instance
```

## List gorups by group type

Groups have a `type`, get details with
```python
client.get_call("feedtype/list") # platform only

client.get_call("feedtype/list", instance="<your_instance>") # one one instance
```

## Create a group

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

group = {
    "customer": "123456789",
    "name": "Display name",
    "functionalInnerId": "any, for external use only",
    "type": "12345678", # feed type
    }
}
new_group = client.get_call("feed/save", body=group:dict)
```

## Update a group

```python
group = client.get_call("feed/get", uid="<feedUid>")

# change group name then save

group = client.get_call("feed/save", body=group:dict)

```

## Delete a group

```python
# user feed/delete with the feed ui

client.get_call("feed/delete", uid="<feedUid>")
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
new_group = api.get_call("feed/save", body=group:dict)
```

Notes:
- you can add one group per identity provider. If you try to add more than one group per idp, the last one will be preserved.
- the group email should exist, in the other case the api will return an error.
- only `google` and `microsoft` idp supports the group synchronization.
- members are retrieved asynchronously by the server, you may need to wait before doing a member list request to have the full list of members.

## List the members of one or many feed

use the user/list endpoint with the feed id in the `feeds` filter.

```python
feed_members = api.get_call("user/list", feeds=feed_ids:list)

```

## update members of a group

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

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

client.get_call("feed/subscribers/save", body=body:dict)
```

## Get all group id

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_all_group_id()
```

## Get public group id

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_public_group_id()
```

## Get group

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_group(group_id="<group_id>")
```

## Add users to group

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.add_users_to_group(feed_id="<feed_id>", user_emails=your_user_emails_list:list)
```

## Add users to group skip missing users

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.add_users_to_group_skip_missing(feed_id="<feed_id>", user_emails=your_user_emails_list:list)
```

## Iter groups

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.iter_groups(type_id="<type_id>")
```

## Add global group

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.add_global_group(grouptype_id="<your_group_type_id>", name="<name>")
```

## Add local group

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.add_local_group(grouptype_id="<your_group_type_id>", name="<name>")
```

## Sync group

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.sync_group(group_id="<your_group_id>")
```

