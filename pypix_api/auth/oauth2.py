import requests
from typing import Dict

class OAuth2Client:
    def __init__(self, token_url: str, client_id: str, client_secret: str, scopes: str, cert: str = None, key: str = None):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.cert = (cert, key) if cert and key else None
        self.token = None

    def get_token(self) -> str:
        data = {
            "grant_type": "client_credentials",
            "scope": self.scopes,
        }
        auth = (self.client_id, self.client_secret)
        response = requests.post(
            self.token_url,
            data=data,
            auth=auth,
            cert=self.cert,
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]
        return self.token
