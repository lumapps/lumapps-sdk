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

## Community get

```python
community = client.get_call(
    "community/get", uid="YOUR_COMMUNITY_ID"
)
```

For more details see [the api documentation](https://api.lumapps.com/docs/lumapps-public-api/0cb3a41bb0afa-retrieve-a-community)
