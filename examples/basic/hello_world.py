from lumapps_api_client.lib import ApiClient
from __init__ import BEARER

user_email = "salah@managemybudget.net"
api = ApiClient(token=BEARER)


if api.token:
    print("Your api token is {}".format(api.token))
    usr = api.get_call("user", "get", email=user_email)

    print("Hello {}".format(usr.get("fullName", "")))


