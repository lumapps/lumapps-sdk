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
