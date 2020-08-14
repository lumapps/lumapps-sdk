# Environment

As your LumApps platform can be on a specific environment you'll need to give the ApiClient the correct base url in order for it to work correctly.

By default the ApiClient uses `https://sites.lumapps.com`. 

To use another base url (you can find more informations about those url [here](https://docs.lumapps.com/docs/home/architecture/archi-lumapps-platform-site-architecture)) you have to do:

```python
from lumapps.api.client import ApiClient

client = ApiClient(api_info={"base_url": <my_base_url>})
```
