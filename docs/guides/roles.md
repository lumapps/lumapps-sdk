# Role

You can easly create, modify, delete or list roles on your instance with the sdk.

## __List roles__

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

roles = client.get_call("role/list", instance=site_id)
 ```

 ## __Create a specific role__

 To create a role you need to create an object like the following one

 ```python
 from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

my_role = {
  "authorizations": authorizations,
  "description": {"fr": "Ma description en francais"},
  "instance": site_id,
  "feeds": ["518815757015446"],
  "name": "My custom role"
}

client.get_call("role/save", body=my_role)
```

Here we have:

* authorization: The authorization associated to that role ([See below](#Authorizations))
* description: A description of the role (can be translated in multiple languages)
* instance: The instance id of the instance where to create that role
* feeds: The ids of the groups that have the rights on that role. **At least one** is required.
* name: The name of the role

### __Authorizations__

```python
authorization_1 =  {
  "actions": actions,
  "feeds": ["518815757015496"],
  "metadata": ["51881575701549"]
}
authorizations = [authorization_1]
```

* actions:  A list of actions ([See below](#Actions))
* feeds: A list of ids of the groups targeted by the given actions
* metadata: A list if ids of the metadatas associated to the givena actions.


### __Actions__

```python
 action_1 = {
  "type": "EDIT",
  "name": "PAGE"
}

action_2 = {
    "type": "READ",
    "name": "PAGE"
}

actions = [action_1, action_2]
```

* type: The type of action. The accepted types are listed below
    ```python
    FEED GROUP GLOBAL USER NEWS NEWSLETTER COMMUNITY CUSTOM ANALYTICS GAMIFICATION DIRECTORY_ENTRY STYLE MEDIA DIRECTORY POST CUSTOM_CONTENT TUTORIAL TARGET RESELLER MENU INSTANCE ROLE TEMPLATE PAGE METADATA
    ```
* name: The name of the action. The accepted names are listed below
    ```python
    READ DROP PUBLISH ADMIN EDIT ARCHIVE DELETE
    ```

## __Update a role__

To update a role the recommanded way is the following:

1. get it
2. change/add the informations you want
3.  re-save it.

```python
 from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

# Get the role
role = client.get_call("role/get", uid=role_uid)

# Update it ...
role["name"] = "New role name"

# Save the updated role
client.get_call("role/save", body=role)
```

## Iter roles

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.iter_roles()
```

## Save role

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.save_role(role=your_role:dict)
```
