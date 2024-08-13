# Communities


## Community list

```python
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
community = client.get_call(
    "community/get", uid="YOUR_COMMUNITY_ID"
)
```

For more details see [the api documentation](https://apiv1.lumapps.com/#operation/Community/Get)
