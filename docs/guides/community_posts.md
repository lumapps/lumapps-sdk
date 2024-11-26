
# Posts

## Post list

```python
body = {
    "contentId": community_id,
    "lang": "",
    }

posts = client.get_call(
    "community/post/search", body=body
)
```

For more details see [the api documentation](https://api.lumapps.com/docs/lumapps-public-api/85ebc4227cf2c-search-for-posts)


## Post get

```python
post = client.get_call(
    "community/post/get", uid="YOUR_POST_ID"
)
```

For more details see [the api documentation](https://api.lumapps.com/docs/lumapps-public-api/cfecfd13ab19d-retrieve-a-post)

## Post save

The variable `post` is a json object described [here](https://api.lumapps.com/docs/lumapps-public-api/2f1f03ecf288d-post).
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

For more details see [the api documentation](https://api.lumapps.com/docs/lumapps-public-api/256b10f9a7a7d-save-a-commmunity)
