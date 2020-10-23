# Authentication

The first thing you'll need in order for you to be able to use the LumApps Api's is a valid token.

You can see them [here](https://apiv1.lumapps.com/#tag/Authentication)

The LumApps sdk can help you when using a service account or a regular token, all you have to do is to give the sdk the credentials infos and the subsequent calls made by the tool will be authenticated using those credentials.

**Note**:

Be sure to target the right lumapps environment, by default the sdk use site.lumapps.com as an environment.
If your env is different (eg, sites-ms.lumapps.com) you can precise it like so:

```python
from lumapps.api.base_client import BaseClient
api_info = {
    "base_url": "https://sites-ms.lumapps.com"
}
client = BaseClient(token="<your_token>", api_info=api_info)
```

## Using a regular token

To authenticate with a regular, short lived token, instanciate the sdk like so:

```python
from lumapps.api.base_client import BaseClient
client = BaseClient(token="<your_token>")
```

## Using an authorized service account

By default a service account does not allows you to contact all LumApps API endpoints, to do so you need to get a token as a given user and then use this token to authenticate the requests

<details>
<summary>An example with curl</summary>
<p>

The flow is as follow:
<br>

<ol>
    <li>
        With your service account get a google access token
        <div style="margin: 8px;">
        To know how to get this token with curl and you service account follow <a href="https://gist.github.com/ryu1kn/c76aed0af8728f659730d9c26c9ee0ed"> this tutorial</a>
        <br/>
        For an extended documentation on that process you can follow the <a href="https://developers.google.com/identity/protocols/oauth2/service-account"> google documentation</a>
        </div>
    </li>
    <li>
        Use this token as the bearer token to call the <a href="https://apiv1.lumapps.com/#operation/User/Gettoken"> user/get endpoint</a>
        <br/>
        <div>
        <pre>
        <code>
        curl -s -X GET https://<you_lumapps_env_base_url>/_ah/api/lumsites/v1/user/getToken?customerId=<my_platform_id>&email=<user_email_I_want_to_autehntify_as> \
            -H "Accept: application/json" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer <the_google_access_token_you_got_previously>"
        </code>
        </pre>
        </div>
    </li>
    <li>
        Use the returned LumApps access token to authenticate your subsequent requests to LumApps Api's.

        <br/>
        For instance you can call the user/get endpoint:
        <div>
        <pre>
        <code>
        curl -s -X GET https://<you_lumapps_env_base_url>/_ah/api/lumsites/v1/user/get \
            -H "Accept: application/json" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer <the_lumapps_access_token_you_got_previously>"
        </code>
        </pre>
        </div>
    </li>
</ol>

</p>
</details>

<details>
<summary>An example with Postman</summary>
<p>

The flow is the same as with curl but to do it with postman there are some specificities and that's why we provide a <a href="../static/get_token_postman_collection.json" >collection that illustrate it</a>.

<br/>

This collection uses <a href="https://learning.postman.com/docs/sending-requests/variables" >postman variables</a> and you have to set some to use it:

<br/>
<ul>
    <li><i>sa_private_key</i>: Private of the service account</li>
    <li><i>sa_email</i>: Service account email</li>
    <li><i>lumapps_base_env_url</i>: The base url of the LumApps env (eg, https://sites.lumapps.com)</li>
</ul>

<br/>

You'll also have to execute in order, the requests are numbered so make sure to execute them from 1 to 4.

</p>
</details>

<details>
<summary>With the LumApps sdk</summary>
<p>

The sdk BaseClient offers two methods to help with that `get_new_client_as` and `get_new_client_as_using_dwd` that allows you to get a new BaseClient correctly authenticated.


```python
from lumapps.api.base_client import BaseClient
my_sa = {...}
my_platform_id="<your_plaform_id>"
user_to_authenticate_on_behalf_of = "<user_email>"

client = BaseClient(
    auth_info=my_sa)
    .get_new_client_as(
        user_email=user_to_authenticate_on_behalf_of,
        customer=platform_id
    )
```
</p>
</details>

**Note**:

The LumApps bearer token you get in that case extends to 24h instead of 1h.
