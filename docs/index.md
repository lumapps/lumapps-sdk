# Lumapps SDK

<p align="center">
    <a href="https://github.com/lumapps/lumapps-sdk/actions?query=workflow%3ACI"><img alt="Action Status" src="https://github.com/lumapps/lumapps-sdk/workflows/CI/badge.svg"></a>
    <a href="https://pypi.org/project/lumapps-sdk/"><img alt="Pypi" src="https://img.shields.io/pypi/v/lumapps-sdk"></a>
    <a href="https://codecov.io/gh/lumapps/lumapps-sdk/branch/master"><img alt="Coverage" src="https://codecov.io/gh/lumapps/lumapps-sdk/branch/master/graph/badge.svg"></a>
    <a href="https://github.com/ambv/black"><img alt="Black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
    <a href="#"><img alt="Black" src="https://img.shields.io/badge/python-3.6%7C3.7%7C3.8-blue"></a>
</p>


LumApps SDK is a set of tools to manipulate the [LumApps API](https://api.lumapps.com/docs/start)

This includes:

- A client that support all the routes of the API (located in folder lumapps)
- A set of helper classes to easily manipulate LumApps elements as Python Objects and classes (folder lumapps/helpers)


## Installation

```bash
pip install lumapps-sdk
```

## Requirements

Python >= 3.7

## Getting started

1. Get your token

    LumApps supports multiple ways of authentication.
    The fastest one to implement is the following:

    Get your token by logging to your LumApps account.
    Go to [https://sites.lumapps.com](https://sites.lumapps.com) and authenticate.
    Once connected, open the javascript console of your browser and run:

    ```javascript
    var instance = window.location.pathname.split('/');
    instance = instance[1] == "a" ? instance[3] : instance[1]
    fetch(window.location.origin+"/service/init?customerHost="+window.location.host+"&instanceSlug="+instance+"&    slug=").then(data=>{return data.json()}).then(res => {console.log(res.token)})
    ```

    This will generate your personal LumApps token that will be active for 60 minutes, and that we will use in the following steps

2. Authenticate

    ```python
    from lumapps.api import BaseClient

    token = "MY TOKEN"
    client = BaseClient(token=token)
    ```

3. Make your first API call

    Let's display the full name of a registered user in lumapps

    ```python
    user_email = "YOUR EMAIL"
    usr = api.get_call("user/get", email=user_email)
    print("Hello {}".format(usr["fullName"]))
    ```

## Documentation

The SDK documentation is available [here](https://lumapps.github.io/lumapps-sdk/).

## Code convention

Docstring in PEP 484 type annotations format adapted to python 2.7 using comments.

## How to get help, contribute, or provide feedback

Please refer to our [contributing guidelines](CONTRIBUTING.md).

## Copyright and license

LumApps SDK is released under the [MIT license](LICENSE.md).
