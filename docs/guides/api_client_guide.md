# Api client

The client exposed by the lumapps-sdk allows you to interact with the lumapps apis more easily, to do so you have 2 mains methods defined in it.

## get_call method

The `get_call` method allows you to call a particular endpoint and get result. This is the main way to call the LumApps apis. 

If you call a `list` endpoint (eg, user/list), this method will fetch all the pages an returns you all the results at once.




## iter_call method

The `iter_call` is an alternative method that will fetch page by page the elements an return them in a python generator.

This can help you manage memory more efficiently.

## Adding query parameters 

To specify *query parameters* allong with the call you have to add them as **kwargs** of the `get_call` (or `iter_call`) method

For instance if you want to get a particular user identified by his email you'll do:

```python
from lumapps.api.client import ApiClient

client = ApiClient(token="<your_token>")

email = "<the_user_email>"
user = client.get_call("user/get", email=email)
```
## Adding request body parameters

To specify *body parameters* allong with the call you have to add them as a dict passed in the **body** parameters of the `get_call` method

For instance if you want to create a particular user:

```python
from lumapps.api.client import ApiClient

client = ApiClient(token="<your_token>")

body = {
    "email": "test@test.com",
    "accountType": "external"
}
saved_user = client.get_call("user/get", body=body)
```