# LumappsClient

## Iter content list

To iterate and list the contents by arguments.

```python
from lumapps.api.client import LumappsClient

api_info = {"base_url": "<your_lumapps_base_url>"}
content_list = LumappsClient(client).iter_content_lists(token=<"your_token">, api_info= api_info, customer_id=<"platform_id">, instance_id=<"instance_id">, content_type_id=content_type_id)
```

## Iter content types

To iter the content types by arguments.

```python
from lumapps.api.client import LumappsClient

api_info = {"base_url": "<your_lumapps_base_url>"}
content_type = LumappsClient(client).iter_content_types(token=<"your_token">, api_info= api_info, customer_id=<"platform_id">, instance_id=<"instance_id">, {"name": "<content type name>"})
```

## Iter users 

To iterate over platform users.

```python
from lumapps.api.client import LumappsClient

api_info = {"base_url": "<your_lumapps_base_url>"}
users = LumappsClient(client).iter_users(token=<"your_token">, api_info= api_info, customer_id=<"platform_id">, instance_id=<"instance_id">,status="enabled")
```

## Get user

Get a user from its id or email

```python
from lumapps.api.client import LumappsClient

api_info = {"base_url": "<your_lumapps_base_url>"}
user = LumappsClient(client).get_users(token=<"your_token">, api_info= api_info, customer_id=<"platform_id">, instance_id=<"instance_id">,id_or_email="1234@fakemail.com")
```

