# LumappsClient

## Iter content list

To iterate and list the contents by arguments.

```python
from lumapps.api.base_client import BaseClient
from lumapps.api.client import LumappsClient

client = BaseClient(token="<your_token>")
content_list = LumappsClient(client).iter_content_lists(content_type_id=content_type_id)
```

## Iter content types

To iter the content types by arguments.

```python
from lumapps.api.base_client import BaseClient
from lumapps.api.client import LumappsClient

client = BaseClient(token="<your_token>")
content_type = LumappsClient(client).iter_content_types({"name": "<content type name>"})
```

## Iter users 

To iterate over platform users.

```python
from lumapps.api.base_client import BaseClient
from lumapps.api.client import LumappsClient

client = BaseClient(token="<your_token>")
users = LumappsClient(client).iter_users(status="enabled")
```

## Get user

Get a user from its id or email

```python
from lumapps.api.base_client import BaseClient
from lumapps.api.client import LumappsClient

client = BaseClient(token="<your_token>")
user = LumappsClient(client).get_users(id_or_email="1234@fakemail.com")
```

