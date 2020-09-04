# Communities


## Community list

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

body = {
    "instanceId": "YOUR_INSTANCE_ID",
    "lang": "fr",
    }

communities = client.get_call(
    "community/list", body=body
)
```

For more details see [the api documentation](https://apiv1.lumapps.com/#operation/Community/List)

## Community get

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

community = client.get_call(
    "community/get", uid="YOUR_COMMUNITY_ID"
)
```

For more details see [the api documentation](https://apiv1.lumapps.com/#operation/Community/Get)
