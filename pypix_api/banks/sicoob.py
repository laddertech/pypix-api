from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.auth.mtls import get_session_with_mtls

class SicoobAPI:
    BASE_URL = "https://api.sicoob.com.br/pix"

    def __init__(self, client_id, client_secret, cert_path, key_path):
        self.oauth = OAuth2Client(
            token_url="https://auth.sicoob.com.br/auth/realms/sicoob/protocol/openid-connect/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes="cob.read cob.write pix.read pix.write",
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
