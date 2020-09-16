# Authentication

The first thing you'll need in order for you to be able to use the LumApps Api's is a valid token.

You can see them [here](https://apiv1.lumapps.com/#tag/Authentication)

The LumApps sdk can help you when using a service account or a regular token, all you have to do is to give the sdk the credentials infos and the subsequent calls made by the tool will be authenticated using those credentials.

**Note**:

Be sure to target the right lumapps environment, by default the sdk use site.lumapps.com as an environment.
If your env is different (eg, sites-ms.lumapps.com) you can precise it like so:


```python
from lumapps.api.client import ApiClient

api_info = {
    "base_url": "https://sites-ms.lumapps.com"
}
client = ApiClient(token="<your_token>", api_info=api_info)
```

## Using a regular token

To authenticate with a regular, short lived token, instantiate the sdk like so:

```python
from lumapps.api.client import ApiClient

client = ApiClient(token="<your_token>")
```

## Using an authorized service account

By default a service account does not allows you to contact all LumApps API endpoints, to do so you need to get a token as a given user and then use this token to authenticate the requests

The sdk ApiClient offers two methods to help with that `get_new_client_as` and `get_new_client_as_using_dwd` that allows you to get a new ApiClient correctly authenticated.


```python
from lumapps.api.client import ApiClient

my_sa = {...}
my_platform_id="<your_plaform_id>"
user_to_authenticate_on_behalf_of = "<user_email>"

client = ApiClient(
    token="<your_token>",
    auth_info=my_sa)
    .get_new_client_as(
        user_email=user_to_authenticate_on_behalf_of,
        customer=platform_id
    )
```


**Note**:

The authentication is that case extends to 24h instead of 1h.
