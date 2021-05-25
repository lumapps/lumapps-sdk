# Tutorial

## Get tutorial

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_tutorial(uid="<tutorial_uid>")
```

## Save tutorial

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.save_tutorial(tutorial=tutorial:dict)
```

