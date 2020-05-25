from lumapps.api import ApiClient


class TokenClient(ApiClient):
    def __init__(self, customer_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer_id = customer_id

    def get_token_and_expiry(self, email):
        resp = self.get_call("user/getToken", customerId=self.customer_id, email=email)
        return resp["accessToken"], int(resp["expiresAt"])

    def get_token_getter(self, email):
        def f():
            return self.get_token_and_expiry(email)

        return f
