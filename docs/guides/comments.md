
## Comments

## Comment list


```python
with_answers = True #False

comments = api.get_call(
    "comment", "list", content="YOUR_POST_ID", withAnswers=with_answers
)
```

For more details see [api.lumapps.com](https://api.lumapps.com/docs/lumapps-public-api/ccd9fdc5fc626-list-comments)

## Comment get

```python
comment = client.get_call(
    "comment/get", uid="YOUR_COMMENT_ID"
)
```

For more details see [api.lumapps.com](https://api.lumapps.com/docs/lumapps-public-api/2704d9935b7b8-retrieve-a-comment)

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
comment = client.get_call(
    "comment/get", uid="YOUR_COMMENT_ID"
)

comment["title"] = {"fr": "New title"}

comment = client.get_call(
    "comment/save", body=comment
)
```

For more details see [the api documentation](https://api.lumapps.com)
