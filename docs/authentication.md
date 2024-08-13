# Authentication

The first thing you'll need in order for you to be able to use the LumApps Api is a valid token.

You can see them [here](https://apiv1.lumapps.com/#tag/Authentication)

The LumApps sdk can help you when using a service account or a regular token, all you have to do is to give the sdk the credentials infos and the subsequent calls made by the tool will be authenticated using those credentials.

Be sure to target the right lumapps environment. Refer to the [environment documentation](https://lumapps.github.io/lumapps-sdk/environment) first.

## Using a regular token

To authenticate with a regular, short lived accesss token, instantiate the sdk like so:

```python
from lumapps.api.base_client import BaseClient

client = base_client = BaseClient(
        api_info={"base_url": "https://your-cell.api.lumapps.com"},
        auth_info={
            "client_id": "your-client-id",
            "client_secret": "your-client-secret"
        }
    )
```

## Using an application

First of all, please create an application following the documentation on the [dev portal](https://developer.lumapps.com/documentation/oauth).

Then, the sdk BaseClient offers one method to retrieve a new authenticated `BaseClient`: `get_new_client_as`.

```python
from lumapps.api.base_client import BaseClient

my_application = {
    "client_id": "<application_client_id>",
    "client_secret": "<application_client_secret>",
}
customer_id = "<your_customer_id>"
user_to_authenticate_on_behalf_of = "<user_email>"
api_info={"base_url": "https://your-cell.api.lumapps.com"} # e.g. https://go-cell-001.api.lumapps.com

client = BaseClient(
    api_info, auth_info=my_application
).get_new_client_as(
    user_to_authenticate_on_behalf_of, customer_id
)
```
