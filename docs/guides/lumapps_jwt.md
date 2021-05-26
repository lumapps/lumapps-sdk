#  LumApps jwt 

If you need to verify the jwt token provided by lumapps the LumApps SDK provide an helper class for that purpose.

It simply decodes the token for you, raise error if there is any problem and return the jwt payload.


```python
from lumapps.api.lumapps_jwt import LumappsJWT
from lumapps.api.errors import LumappsJWT

jwt_checker = LumappsJWT()
token = "<your_token>"

try:
    decoded_token = jwt_checker.decode(token)
expect LumAppsJwtTokenExpiredError:
    print(f"The token expired ...")
```