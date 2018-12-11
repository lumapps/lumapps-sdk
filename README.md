
*Please be aware the this sdk is still in beta version (0.1) and is undergoing a fast paced evolution that may break changethe behaviour of some helpers*

*Make sure of the version you are using (Git tags & releases)*

----
[![Build](https://circleci.com/gh/aureldent/lumapps-sdk.svg?style=svg)](https://circleci.com/gh/aureldent/lumapps-sdk)
[![Documentation Status](https://readthedocs.org/projects/pip/badge/?version=stable)](http://pip.pypa.io/en/stable/?badge=stable)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![coverage](https://codecov.io/gh/aureldent/lumapps-sdk/branch/master/graph/badge.svg)](https://codecov.io/gh/aureldent/lumapps-sdk)
[![Known Vulnerabilities](https://snyk.io/test/github/aureldent/lumapps-sdk/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/aureldent/lumapps-sdk?targetFile=requirements.txt)

Lumapps SDK is a set of tools to manipulate the [LumappsAPI](http://api.lumapps.com)
This includes a client that support all the routes of the API (located in folder lumapps_api_client)
and a set of helper classes to easily manipulate Lumapps elements as Python Objects and classes (folder lumapps_api_helpers)


## Quick start

<!---2 quick start options are available:
 [Download the latest release](../../release). -->

### Installation

```
git clone https://github.com/lumapps/lumapps-sdk.git
cd lumapps-sdk
pip install -e .
```

### Getting started

Lumapps supports multiple ways of authentification.
The fastest one to implement is the following:

Get your token by logging to your Lumapps account.
Go to [https://sites.lumapps.com](https://sites.lumapps.com) and authentificate.
Once connected, open the javascript console of your browser and run:

```javascript
var instance = window.location.pathname.split('/');
instance = instance[instance.length-2];
fetch(window.location.origin+"/service/init?customerHost="+window.location.host+"&instanceSlug="+instance+"&slug=").then(data=>{return data.json()}).then(res => {console.log(res.token)})
```

This will generate your personal Lumapps token that will be active for 60 minutes, and that we will use in the following steps

#### Authentification

```python

from lumapps_api_client.lib import ApiClient

token = "MY TOKEN"
api = ApiClient(token=token)

```

#### Your first API call

Let's display the full name of a registered user in lumapps

```python

user_email = "YOUR EMAIL"
usr = api.get_call("user", "get", email=user_email)
print("Hello {}".format(usr.get("fullName", "")))

```


## Documentation

The SDK documentation is available in the [the wiki](../../wiki)
The folder "examples" also provides some basic examples to manipulate the sdk

<!-- ### Running documentation locally

You can build and compile the source documentation using Sphinx. This documents the methods of the SDK
First install the dev dependencies (reqirements_dev.txt) and run

```python

sphinx-build -b html documentation/source documentation/build

```
-->

### Code convention

Docstring in PEP 484 type annotations format adapted to python 2.7 using comments.


## Copyright and license

Code and documentation copyright 2018 LumApps. Code released under the [MIT license](LICENSE.md).


## How to get help, contribute, or provide feedback

Please refer to our [contributing guidelines](CONTRIBUTING.md).
