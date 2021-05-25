
# Posts

## Post list

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

body = {
    "contentId": community_id,
    "lang": "",
    }

posts = client.get_call(
    "community/post/search", body=body
)
```

For more details see [the api documentation](https://apiv1.lumapps.com/#operation/Community%20Post/Search)


## Post get

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

post = client.get_call(
    "community/post/get", uid="YOUR_POST_ID"
)
```

For more details see [the api documentation](https://apiv1.lumapps.com/#operation/Community%20Post/get)

## Post save

The variable `post` is a json object described [here](https://api.lumapps.com/docs/output/_schemas/post.html).
You can either construct a new one from scratch:
```python
post = {
    "customer": "YOUR_CUSTOMER_ID",
    "instance": "YOUR_INSTANCE_ID",
    "type": "post",
    "postType": "[DEFAULT|IDEA|QUESTION]",
    "externalKey": "YOUR_COMMUNITY_ID",
    "title": {"fr": "Some post title"},
    "content": {"fr": "Post content, you can use markdown"},
    "publicationDate": publication_date,
    "createdAt": publication_date,
    "startDate": publication_date,
    "version": 1,
}
```

or update properties from one you just got using the api.

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

post = client.get_call(
    "community/post/get", uid="YOUR_POST_ID"
)

# Modify the post
post["tttle"] = {"fr": "New title"}

# Save the post
post = api.get_call(
    "community/post/save", body=post
)
```

For more details see [the api documentation](https://apiv1.lumapps.com/#operation/Community%20Post/save)

## Iter community posts

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.iter_community_posts(community_id="<your_community_id>")
```

## Iter posts 

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.iter_posts(community_id="<your_community_id>")
```

## Pin post 

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.pin_post(community_id="<your_community_id>", post_id="<post_id>")
```

## Delete post 

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.delete_post(post_id="<post_id>")
```

## Save post 

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.save_post(post=post:dict)
```

## Get post 

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_post(post_id="<your_post_id>")
```