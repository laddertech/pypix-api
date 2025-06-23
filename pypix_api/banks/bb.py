from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.auth.mtls import get_session_with_mtls

class BancoDoBrasilAPI:
    BASE_URL = "https://api.bb.com.br/pix/v1"

    def __init__(self, client_id, client_secret, cert_path, key_path):
        self.oauth = OAuth2Client(
            token_url="https://oauth.bb.com.br/oauth/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes="pix.read pix.write",
            cert=cert_path,
            key=key_path,
        )
        self.session = get_session_with_mtls(cert_path, key_path)

    def get_cobrancas(self):
        token = self.oauth.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        resp = self.session.get(f"{self.BASE_URL}/cob", headers=headers)
        resp.raise_for_status()
        return resp.json()
