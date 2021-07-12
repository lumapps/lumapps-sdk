# Folder

## Get personal folder

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_personal_folder(name="<folder_name>")
```

## Get instance folder

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_instance_folder(name="<folder_name>")
```

## Get folder by name

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_folder_by_name(name="<folder_name>", shared= True:bool)
```

## Create or get personal folder

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.create_or_get_personal_folder(name="<folder_name>", author="<author_name>")
```

## Create or get instance folder

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.create_or_get_instance_folder(name="<folder_name>", author="<author_name>")
```

## Create or get folder by name

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.create_or_get_folder_by_name(name="<folder_name>", shared=True:bool, author="<author_name>")
```

## Create folder

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.create_folder(name="<folder_name>", shared=True:bool, parent_id="<parent_id>")
```

## Save folder

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.save_folder(folder=your_folder:dict)
```

## Iter folders

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.iter_folders(lang="<language>"(optional))
```

## Get folder

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_folder(folder_id="<folder_id>")
```