
## Comment list


```python
with_answers = True #False

comments = api.get_call(
    "comment", "list", content="YOUR_POST_ID", withAnswers=with_answers
)
```

For more details see [api.lumapps.com](https://apiv1.lumapps.com/#operation/Comment/List)


## Iter root comments of a content

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.iter_root_comments(content_id="<your_content_id>")
```

## Iter replies of a content

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.iter_replies(content_id="<your_content_id>")
```

## Iter comments of a content

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.iter_comments(content_id="<your_content_id>")
```

## Comment get

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

comment = client.get_call(
    "comment/get", uid="YOUR_COMMENT_ID"
)
```

For more details see [api.lumapps.com](https://apiv1.lumapps.com/#operation/Comment/Get)

## Comment save

The variable `comment` is a json object described [here](https://api.lumapps.com/docs/output/_schemas/comment.html).
You can either construct a new one from scratch:

```python

comment = {
    "content": "YOUR_POST_ID",
    "customer": "YOUR_CUSTOMER_ID",
    "instance": "YOUR_INSTANCE_ID",
    "text": {
        {"fr": "Comment content, you can use markdown"},
    },
    "publicationDate": publication_date,
    "createdAt": publication_date,
    "startDate": publication_date,
}
```

or update properties from one you just got using the api.

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")

comment = client.get_call(
    "comment/get", uid="YOUR_COMMENT_ID"
)

comment["title"] = {"fr": "New title"}

comment = client.get_call(
    "comment/save", body=comment
)

For more details see [the api documentation](https://apiv1.lumapps.com)
```

## Mark comment as relevant

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.mark_comment_as_relevant(comment_id="<your_comment_id>")
```

## Hide comment

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.hide_comment(comment="<dict(your_comment)>")
```

## Like comment

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.like_comment(comment="<dict(your_comment)>")
```