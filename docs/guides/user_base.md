# Users

## List all your LumApps platform users

To list the users of your platform we'll use the [/user/list]() endpoint.

To get all users at once you can use the `get_call` method provided by the BaseClient.

```python
from lumapps.api.client import BaseClient

client = BaseClient(token="<your_token>")

users = client.get_call("user/list")
```

You can also add additional parameters according to the [documentation](https://apiv1.lumapps.com/#operation/User/List)

For instance, if you want to list the users of your platform but filter only the ones that are enabled you will do

```python
from lumapps.api.client import BaseClient

client = BaseClient(token="<your_token>")

users = client.get_call("user/list", status="enabled")
```
Alternatively you can fetch these users page by page using the `iter_call` method.

## Get a particular user

To get a particular user you can do:

```python
from lumapps.api.client import BaseClient

client = BaseClient(token="<your_token>")

email = "<the_user_email>"
user = client.get_call("user/get", email=email)
```

## Get the authenticated user

To get the user authenticated by the token you provided to the BaseClient you can do:

```python
from lumapps.api.client import BaseClient

client = BaseClient(token="<your_token>")

me = client.get_call("user/get")
```

## Create a new user

```python
from lumapps.api.client import BaseClient

client = BaseClient(token="<your_token>")

body = {
    "email": "test@test.com",
    "accountType": "external"
}
saved_user = client.get_call("user/save", body=body)
```

## Update an existing user

To update an existing user the best pratice is to get it, modify it and then save it.

```python
from lumapps.api.client import BaseClient

client = BaseClient(token="<your_token>")

# Get tge user
email = "<user_email>"
user = client.get_call("user/get", email=email)

# Update it
user["firstName"] = "Jacques"

# save it
saved_user = client.get_call("user/save", body=user)
```

## Deactivate a user

To deactivate a user you need to set his status to `disabled`

```python
from lumapps.api.client import BaseClient

client = BaseClient(token="<your_token>")

# Get tge user
email = "<user_email>"
user = client.get_call("user/get", email=email)

# Update his status
user["status"] = "disabled"

# save it
saved_user = client.get_call("user/save", body=user)
```