# Content type

## Content type list
The `instance` paramenter is mandatory for this call.

```python
from lumapps.api.base_client import BaseClient
client = BaseCLient(token="<your_token>", api_info="<api_info">)

content_types = client.get_call("customcontenttype/list", instance="<your_instance_id>")
```
## Get content type
Get detail of a custom content type

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_content_type(content_type_id="<your_content_type_uid>")
```

## Get News content type
Get News content type 

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_news_content_type()
```

## Get Page content type
Get Page content type 

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_page_content_type()
```

## Iter content type
Iter content type with arguemnts

You can add more filters, see [apidoc](https://apiv1.lumapps.com/#operation/Customcontenttype/List)

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.iter_content_types({"lang": "en"})
```

## Save a content type
Save a custom content type

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

content_type_dict = 
    {
        "customer": "string(Required)",
        "hasFeaturedStartDate": true,
        "heritable": true,
        "name": "string",
        "heritableLocked": true,
        "createFromScratchLocked": true,
        "isWorkflowEnabled": true,
        "isEndDateMandatory": true,
        "functionalInnerId": "string",
        "instance": "string",
        "endDateDelta": 0,
        "updatedAt": "string",
        "notifyContributors": true,
        "uid": "string",
        "parentCustomContentType": "string",
        "tags": [
            {
            "uid": "string",
            "uuid": "string",
            "id": "string",
            "name": "string",
            "functionalInnerId": "string"
            }
        ],
        "hasFeaturedEndDate": true,
        "workflowManagers": [
            "string"
        ],
        "id": "string",
        "createdAt": "string",
        "icon": "string"
    }

result = client.save_content_type(ct=content_type_dict)
```

