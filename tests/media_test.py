import unittest
import mock
import json

from apiclient.http import HttpMock
from apiclient.discovery import build

from lumapps_api_client.lib import ApiClient
from lumapps_api_helpers.media import list_medias, uploaded_to_media


class TestMedia(unittest.TestCase):
    # def setUp(self):
    #     credentials = mock.Mock(spec="google.oauth2.credentials.Credentials")
    #     self.client = ApiClient("test@test.com", credentials=credentials)
    #     http = HttpMock("test_data/lumapps_discovery.json", {"status": "200"})
    #     service = build("lumapps", "v1", http=http, developerKey="no")
    #     self.client._service = service

    # def test_uploaded_to_media(self):
    #     # Test when name is given
    #     with open("test_data/uploaded_file.json", "r") as f:
    #         uploaded_file = json.load(f)
    #     lang = "en"
    #     instance = "20392"
    #     name = "test"
    #     media = uploaded_to_media(uploaded_file, instance, lang, name)
    #     assert media["content"][0]["value"] == uploaded_file["blobKey"]
    #     assert media["content"][0]["name"] == name
    #     assert media["content"][0]["lang"] == lang
    #     assert media["name"] == {lang: name}
    #     assert media["instance"] == instance

    #     # Test when name is not given
    #     media = uploaded_to_media(uploaded_file, instance, lang)
    #     assert media["content"][0]["value"] == uploaded_file["blobKey"]
    #     assert media["content"][0]["name"] == uploaded_file["name"]
    #     assert media["content"][0]["lang"] == lang
    #     assert media["name"] == {lang: uploaded_file["name"]}
    #     assert media["instance"] == instance

    def test_truc(self):
        creds = {
            "type": "service_account",
            "project_id": "lumapps-apiclient",
            "private_key_id": "72125bd0e8d1b31c572fef374f4d91c19353523d",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDBuWb+MWO+t97Q\n0ttLQUvul0y8Zf4bZXH7RNzNeaxy2j2sbInnyv+GQtpbXKtlGup/nXdDKXNveZWk\nc60nbbeZ9pLH/bsQr4+egobRQsUUrSz7mCorZkfCdZksRHtsSCax1lRKJTEKR9l3\nImLGNLp05aMrfOORO2iL9I4ni1xhuWhHnGQ0Ry5z0Rj+rVNS7CdRIlyrWlawkW64\nQm1Lbz08m865HRZSFC0BiubE6emTbTmtyNg+PbtGY/sDw+0RSAz7NrbCPPdjVijk\nGTo1wl6e6yNiYYye29ZQrz+YENoIVGvGhj0CP4/NSnw8fgNXxaoJa+8mQi6ms72b\nRad1YdHjAgMBAAECggEAKZukn1wETGY5mShwqU0w/eHJPX26gi/bt1gnBIrpmxF8\nxZfaVsqm7zNUquLQfTq2uwobH3W7sWmv1k5yFlHeaVcoV4QLtZ2/fxAR3Mg2hCZd\nzvvzsraZGw8fAv8Cc1Nb3D5ohDRQwCCGeKwOAvw4P/tCfIiqZ/sWjVjNX3jzMpm8\nObn6Dd3OHAnYAffl3ktiPRsHsDVv/PFcZxAtr4W4SoZGkCpLFaje2LtGVgWeUPYV\niR07OCH+ZIxcAt/T7rM94ZKMWrjlINEUSDtYcF9NdAbhWcYmTLrSgqOg9kN+hBMg\nAtjKXTg8C7fgV15GEazvXDz2PramsoiHF1+7/qFpQQKBgQDjHGYU+wO3CJ9Yg7i8\noVy6xKlr1zwg3r+/z6/W51V26o4r7IH2NfMkyfbq9gs4JHilfLE2FwPLSdfMHShJ\nZ9/DRL1FG8+k76T4bFR3MoBcL1pQffVrwv68pX5HxR1blM9YVxElcdf72ZdZtQ2F\nBTZ68klk/oMVAxZfs+7aWE46ewKBgQDaXc3+L3Hz7f75FORLy8yrB8HR2hAX8xzz\n8EX4Y0+vLqathYQBVp6DWaiD9/kqzYU6p1SEcn+Vg7xnqHvxYiEhQAhubRQ1ZPT4\nbZc1mIqUKYDd8CTVgync+GkjAHup9l0QIDhl8yYnjvH87p8Gpy7radftiOvjIR53\nAOUbkMr9uQKBgGd+ZIKBFONO2ZZziDblbaVqwy3yimMMPuNA2IedKdQj9R/NCjhR\nw3hrVMsjzl8KN7RqCzNz73WvM9i/HMG+xTht1bZtgwVNc6cFbsRWzim0Jnrxu2od\nFQqQe+hmygcW3BoMqzKeG2eYc6EcoYmRo48JZCrS1Jc5rfN0wo7bmOKLAoGASyYh\nMCrv0nzDVMEl2Bfo9asTvr6G71cRTboQumyjDazGW80pIrTGlHmUjuYV7+8OvKK9\naV9mHPRbMGlBTk7xC9pXjHkpjT6TN7OvaBh5CIhH+xkb9AbRr2Ql+o+9/z3zxQrx\nndRR+ycsjFkqjUWX1hh04SBP3biWHWpHbnckBLECgYB8+dBHjJImJ9KkRoUQsdjl\nBzK2keQQmPoVxeP5CgSfLXXJZL+4r310L8bAQ2QsINaFAvqOoCbLJEr5BjXq9wU3\npd2n/MqxjLqVW31+xoy2dXxfKhFIascAd7vEGpAJn32+yfoFuenzAGpGAoyKNiCg\n+lKL6tRpNWpkXQoSGPi8OQ==\n-----END PRIVATE KEY-----\n",
            "client_email": "global@lumapps-apiclient.iam.gserviceaccount.com",
            "client_id": "100953606534901570820",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/global%40lumapps-apiclient.iam.gserviceaccount.com"
        }
        client = ApiClient(user="aurelien@managemybudget.net", auth_info=creds)
        from lumapps_api_helpers.media import upload_and_save
        files = ["/home/aurelien/Lumapps/SDK/presentation-sdk-16-01-2018/medias/Tour.jpeg"]
        m = upload_and_save(client, "4684057579618304", files)
        print(m)
        assert False