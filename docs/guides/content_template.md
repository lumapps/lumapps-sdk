# Content template

This notebook aims to explain roughtly how to manipulate a template from LumApps with the LumApps SDK.

The use case could be to use get a given template, fill it with your content and save it as a new content on your site.

## First step - get the template id

After your created your content get's is content id.

The id is in the url of your template
https://your_instance/content/edit/6677628373958656?isTemplate=true

Here our template id is ``6677628373958656``

<img src="https://i.ibb.co/KmzVdW3/template.png" width=800, height=400>

This example as 2 rows with each one containing 2 columns.

## Second step - Get the template in python

```python
import copy
from lumapps.api.client import BaseClient

client = BaseClient(token="{your_token}")

template_id = "{your_template_id}"
template = client.get_call("template/get", uid=template_id)

# We copy it to keep the original as is and maybe use it later to fill it with different content
template_copy = copy.deepcopy(template)
```

Now you have the template.

A template is a big json object that can be seen as:

* Template => Components => Cells => Widgets

or

* Template => Rows => Columns => Widgets

So for instance if I want all the widgets of the `first row` and `second column` I do:

[In]:
```python
first_row_second_column = template_copy['components'][0]['cells'][1]['components']

# Print the type of the widgets in that column
for widget in first_row_second_column:
    print(widget['widgetType'])
```
[Out]:

    html
    user
    content-list


## Third step - modify the template in place

Now that we have the content and know how it is layed out, replacing it should be easy. We just have to found where in each widget the content is and replace it.

**The thing is that some widgets have particularities and so the content is not always in the content key**


The content for an `html` is in the properties of each widget and it's a dictionnary with keys that are the language.

[In]:
```python
first_row_second_column[0]['properties']['content']
```
[Out]:



    {'fr': ['<p> Modified button </p>']}



Whereas the content for a `user_list` is a list of ids and its under the userIds key

[In]:
```python
first_row_second_column[1]['properties']['usersIds']
```
[Out]:



    ['5993218790653952']



Another case is the content for a `content list` is a list of ids and its under the contents key

[In]:
```python
first_row_second_column[2]['properties']['contents']
```
[Out]:



    ['5145730009006080']



So now let change something in the template


```python
first_row_second_column[0]['properties']['content']['fr'] = '<p> Modified button </p>'
```

So, now we can replace this content and so we'll have a template object filled with what we want.

## Fourth step - Save the template in a content

The last step is to save the actual content, so we have to create the basic object for a content and add to it the filled template

The only annoying step before is to get the ids of the feeds we restrict this content to. This is required by the API.

[In]:
```python
instance = "{your_instance_id}"
customer = "{your_customer_id}"

group_name="ALL"
grp_id=client.get_call("feed/search", body={"query": group_name, "instance": instance})[0]['id']
grp_id
```
[Out]:



     '5670405876482048'


Let save it

[In]:
```python
BASE_CONTENT = {
    "type": "custom",
    "feedKeys": [],
    "customer": "",
    "instance": "",
    "customContentType": "",
    "slug": {"fr": ""},
    "template": {},
    "title": {"fr": ""}}

content = copy.deepcopy(BASE_CONTENT)
content['customContentType'] = template_copy['customContentType']
content['template'] = template_copy
content['feedKeys'] = [grp_id]
content['instance'] = instance
content['customer'] = customer
content['title']['fr'] = 'My title' # Modify it
content['slug']['fr'] = "my-custom-content-mdrr" # Modify it

content = client.get_call("content/save", body=content)
if(content.get('status') == 'LIVE'):
    print("Done")

```
[Out]:

    Done


## Result
<img src="https://i.ibb.co/xsjZ3rx/content.png" width=800, height=400>
