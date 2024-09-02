# Lumapps SDK

<p style="text-align:center">
    <a href="https://github.com/lumapps/lumapps-sdk/actions?query=workflow%3ACI"><img alt="Action Status" src="https://github.com/lumapps/lumapps-sdk/workflows/CI/badge.svg"></a>
    <a href="https://pypi.org/project/lumapps-sdk/"><img alt="Pypi" src="https://img.shields.io/pypi/v/lumapps-sdk"></a>
    <a href="https://codecov.io/gh/lumapps/lumapps-sdk/branch/master"><img alt="Coverage" src="https://codecov.io/gh/lumapps/lumapps-sdk/branch/master/graph/badge.svg"></a>
    <a href="https://github.com/ambv/black"><img alt="Black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
    <a href="#"><img alt="Black" src="https://img.shields.io/badge/python-3.8%7C3.9-blue"></a>
</p>


LumApps SDK is a set of tools to manipulate the [LumApps API](https://apiv1.lumapps.com/)

This includes:

- A client that support all the routes of the API (located in folder lumapps)
- A set of helper classes to easily manipulate LumApps elements as Python Objects and classes (folder lumapps/helpers)


## Installation

```bash
pip install lumapps-sdk
```

## Requirements

Python >= 3.8

## Getting started

1. Set up your OAuth application

    Before anything else, you need to set up an OAuth application by following the steps in the [LumApps Developer Portal](https://developer.lumapps.com/documentation/oauth.html).

2. Authenticate

    Once your application set up, get a hand on its client ID and secret, then you can write the following
    to get an access token for a particular user.
    ```python
    from lumapps.api import BaseClient

    token = "MY TOKEN"
    base_client = BaseClient(
        api_info={"base_url": "https://your-cell.api.lumapps.com"}, # e.g. "https://go-cell-001.api.lumapps.com"
        auth_info={
            "client_id": "your-client-id",
            "client_secret": "your-client-secret"
        }
    )

    api = base_client.get_new_client_as("user.email@yourcompany.com", customer_id="your-organization-id")
    ```

3. Make your first API call

    Let's display the full name of a registered user in lumapps

    ```python
    usr = api.get_call("user/get", email="user.email@yourcompany.com")
    print("Hello {}".format(usr["fullName"]))
    ```

## Documentation

The SDK documentation is available [here](https://lumapps.github.io/lumapps-sdk/).

## Code convention

Docstring in PEP 484 type annotations format adapted to python 3.x using comments.

## How to get help, contribute, or provide feedback

Please refer to our [contributing guidelines](CONTRIBUTING.md).

## Copyright and license

LumApps SDK is released under the [MIT license](LICENSE.md).
