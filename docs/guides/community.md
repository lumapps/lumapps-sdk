# Communities


## List communities

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

## Get community

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

community = client.get_call(
    "community/get", uid="YOUR_COMMUNITY_ID"
)
```

For more details see [the api documentation](https://apiv1.lumapps.com/#operation/Community/Get)

## Add categories to community

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.add_categories_to_community(community=community:dict, categories=categories:list>")
```

## Iter communities

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.iter_communities()
```

## Save community layout

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.save_community_layout(community=community:dict)
```

## Get community slug

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_community_slug(community_id="<community_id>")
```

## Delete community

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.delete_community(community_id="<community_id>")
```

## Get community by slug

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_community_by_slug(slug="<slug>")
```

## Save community

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.save_community(community=community:dict)
```