
## Comments

## Comment list


```python
with_answers = True #False

comments = api.get_call(
    "comment", "list", content="YOUR_POST_ID", withAnswers=with_answers
)
```

For more details see [api.lumapps.com](https://apiv1.lumapps.com/#operation/Comment/List)

## Comment get

```python
from lumapps.api.client import ApiClient

client = ApiClient(token="<your_token>")

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
from lumapps.api.client import ApiClient

client = ApiClient(token="<your_token>")

comment = client.get_call(
    "comment/get", uid="YOUR_COMMENT_ID"
)

comment["title"] = {"fr": "New title"}

comment = client.get_call(
    "comment/save", body=comment
)

For more details see [the api documentation](https://apiv1.lumapps.com)
