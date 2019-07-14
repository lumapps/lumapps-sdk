from lumapps.client import LumAppsApiClient

bearer = "yo29.NZmpd29Z6O+7WUt3WirBXWAJbt5xTjawlg8lIG6JfysRj/Mv3Z2j3JvEDZNNKWNY2R8/4psnGTzxdU/E0DgqntTm4msRGtIPVFMA/OqVofA="
# def test_user_get():
#     client = LumAppsApiClient(token=bearer)
#     user = client.api_call("user/get", "GET")
#     print(user)
#     assert False

# def test_user_list():
#     client = LumAppsApiClient(token=bearer)
#     users = client.api_call("user/list", "GET")
#     print(users)
#     for u in users["items"]:
#         _id = u.get("id")
#         print(f"New {_id}")
#     assert False

# def test_user_list():
#     client = LumAppsApiClient(token=bearer)
#     users = client.list_all("user")
#     print(len(users))
#     assert False


def test_user_iter_list():
    client = LumAppsApiClient(token=bearer)
    users = client.iter_list("user")
    print(users)
    for u in users:
        print(u.get("id"))
    assert False
