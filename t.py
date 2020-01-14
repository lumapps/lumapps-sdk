from lumapps.client import LumAppsApiClient

token = "yo29./S8JaJkECBsNaS4LiBartwfGmT33bCA0Bh0otXp+/VCAkaZmr/i+JrEkn5soma2C+gpj5EgXa8zzjxlMs7HjqxtWfI8rhaxOXEI7Ci2axUokK+vIm0+k79CzTnq0btx5GxToIsBASPDoqY8d+VUnrIoyheqvmqLkoUyJb21tCef0cG9N2oVI26IgAiP0WxC968cThQou2aBLBpzne+bOlUzs/uLnIkvSuqNogm9sUpE="
client = LumAppsApiClient(token=token)

print(client.get_call("user/get", email="aurelien@test.lumapps.com"))
