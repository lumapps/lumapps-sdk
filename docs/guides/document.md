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

result = client.get_folder_by_name(name="<folder_name>", shared=bool)
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

result = client.create_or_get_folder_by_name(name="<folder_name>", shared=bool, author="<author_name>")
```

## Create folder

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.create_folder(name="<folder_name>", shared=bool, parent_id="<parent_id>")
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

result = client.iter_folders(lang="<language>": optional)
```

## Get folder

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.get_folder(folder_id="<folder_id>")
```

# Document


## Upload file

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.upload_file(name="<name>", f="<fileIO>", folder_id="<folder_id>", mime_type="<mime_type>")
```

## Upload file to SharePoint

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.upload_file_to_sp(name="<name>", f="<fileIO>", sp_drive_id="<SharePoint_drive_id>", folder_id="<folder_id>", fsize=int)
```

## Upload document

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.update_document(document=your_document:dict)
```

## Delete document

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.delete_document(doc_path="<your_doc_path>")
```

## Iter files

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.iter_files(lang="<lang>": optional)
```

## Iter documents

```python
from lumapps.api.client import LumAppsClient
client = LumAppsClient(token="<your_token>", api_info="<api_info">, customer_id="<customer_id>", instance_id="<instance_id>")

result = client.iter_documents(lang="<lang>": optional, search_text="<search_text>":optional, author="<author>": optional, incl_folders="<incl_folders:bool>": optional, incl_files="<incl_files:bool>": optional, folder_id="<folder_id>", shared="<shared:bool>": optional, trashed="<trashed:bool>": optional, recursive="<recursive:bool>": optional)
```
