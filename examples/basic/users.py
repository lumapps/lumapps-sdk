from lumapps_api_client.lib import ApiClient
from __init__ import BEARER


api = ApiClient(token=BEARER)
users = []
max_users = 50

usrs_iter = api.iter_call("user", "list")

for usr in usrs_iter:
    if len(users) >= max_users:
        break
    users.append(usr)

users = [user.get("uid", "") for user in users if len(users) > 0]

print("{} first users id {}".format(max_users, users))
