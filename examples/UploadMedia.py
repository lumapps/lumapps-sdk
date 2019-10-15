"""
    This is an example of how to upload one or several media(s)
    to your LumApps instance.
"""
from lumapps.api import ApiClient
from lumapps.helpers.media import upload_and_save

TOKEN = "<your_token>"
client = ApiClient(token=TOKEN)

instance_id = "<your_instance_id>"
files = ["<filename 1>", "<filename 2>"]

upload_and_save(client, instance=instance_id, files=files)
