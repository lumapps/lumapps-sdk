# Metadata

## Metadata kind

```python
from lumapps.api.client import ApiClient

client = ApiClient(token="<your_token>")

metadata_kind = client.get_call("metadata/list", body={
    "emptyParent": "true",
    "lang": "fr",
})


print(metadata_kind)
>>> [{
    "customer": "5678444713082880",
    "multiple": "false",
    "isVisibleFront": "false",
    "displayInFilter": "false",
    "instance": "6660333004128256",
    "sortOrder": "22",
    "updatedAt": "2019-04-03T14:07:10.672665",
    "uid": "6298100337213440",
    "heritable": "false",
    "familyKey": "6298100337213440", # <- same Id
    "id": "6298100337213440",        # <- same Id
    "createdAt": "2019-04-03T14:07:10.672871",
    "name":{
        "en": "content",
        }
    }]
```

## Metadata values

```python
from lumapps.api.client import ApiClient

client = ApiClient(token="<your_token>")

metadata_values = client.get_call('metadata', 'list', body={
    "familyId":	"6298100337213440",  # <- /!\
    "parent": "6298100337213440",  # <- /!\
    "lang":"fr",
})

print(metadata_values)
```

```json
[
  {
    "customer": "5678444713082880",
    "multiple": false,
    "isVisibleFront": false,
    "displayInFilter": false,
    "instance": "6660333004128256",
    "sortOrder": "0",
    "updatedAt": "2019-04-03T14:07:18.363623",
    "uid": "5631838787469312",
    "id": "5631838787469312",
    "heritable": false,
    "parent": "6298100337213440", # <- /!\
    "familyKey": "6298100337213440", # <- /!\
    "createdAt": "2019-04-03T14:07:18.363833",
    "name": { "en": "C1" }
  },
  {
    "customer": "5678444713082880",
    "multiple": false,
    "isVisibleFront": false,
    "displayInFilter": false,
    "instance": "6660333004128256",
    "sortOrder": "1",
    "updatedAt": "2019-04-03T14:07:23.464679",
    "uid": "5428492134776832",
    "id": "5428492134776832",
    "heritable": false,
    "parent": "6298100337213440",
    "familyKey": "6298100337213440",
    "createdAt": "2019-04-03T14:07:23.464777",
    "name": { "en": "C2" }
  }
]
```
 

## Metadata Sorting

The `sortOrder` property store a relative position of the element in the list.

To reorder a list, you have to save each element with in the `sortOrder` property the value of the **new index** (the one in the new list).

The initial list

    'element': 'A', sortOrder: -5
    'element': 'B', sortOrder: -4
    'element': 'C', sortOrder: -3
    'element': 'D', sortOrder: -2
    'element': 'E', sortOrder: -1
    'element': 'F', sortOrder: 1
    'element': 'G', sortOrder: 2

Reorder my list

    'element': 'G', sortOrder: 2
    'element': 'F', sortOrder: 1
    'element': 'E', sortOrder: -1
    'element': 'D', sortOrder: -2
    'element': 'C', sortOrder: -3
    'element': 'B', sortOrder: -4
    'element': 'A', sortOrder: -5

Update indexes

    'element': 'G', sortOrder: 1
    'element': 'F', sortOrder: 2
    'element': 'E', sortOrder: 3
    'element': 'D', sortOrder: 4
    'element': 'C', sortOrder: 5
    'element': 'B', sortOrder: 6
    'element': 'A', sortOrder: 7

save each element,
**and wait a few seconds (4-5) between 2 saves**

Code sample

```python
import time

from lumapps.api.client import ApiClient

client = ApiClient(token="<your_token>")

# Get metadata list
metadata_list = client.get_call(
    "metadata/list", 
    instance=SITE_ID, 
    familyId=METADATA_ID, 
    parent=METADATA_ID
)

# sort the list by the english name
def key(meta):
    return meta['name']['en'].lower()
metadata_list = sorted(metadata_list, key=key)

# recompute new index and save each metadata
for index, metadata in enumerate(metadata_list):
    print(f"Saving metadata {metadata['name']}")
    metadata['sortOrder'] = index
    client.get_call("metadata/save", body=metadata)
    time.sleep(4)  # important to let the server recompute new indexes
```
