# Environment

As your LumApps platform can be on a specific environment you'll need to give the BaseClient the correct base url in order for it to work correctly.

This information can be found in the debug dialog in the customer platform (**CTRL + ?** or **CTRL + SHIFT + ?**) in `Haussmann Cell`.

It should be under the following format: `https://XX-cell-YYY.api.lumapps.com`.


```python
from lumapps.api.client import BaseClient

client = BaseClient(
    api_info={"base_url": "https://go-cell-001.api.lumapps.com"},
    auth_info={
        "client_id": "your-client-id",
        "client_secret": "your-client-secret"
    }
)
```
