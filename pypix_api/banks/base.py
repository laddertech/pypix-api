from abc import ABC, abstractmethod
from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.auth.mtls import get_session_with_mtls

class BankPixAPIBase(ABC):
    """Classe base abstrata para clientes Pix de bancos."""

    BASE_URL = None
    TOKEN_URL = None
    SCOPES = None

    def __init__(self, client_id, client_secret, cert_path, key_path):
        if not self.BASE_URL or not self.TOKEN_URL or not self.SCOPES:
            raise ValueError("BASE_URL, TOKEN_URL e SCOPES devem ser definidos na subclasse.")
        self.oauth = OAuth2Client(
            token_url=self.TOKEN_URL,
            client_id=client_id,
            client_secret=client_secret,
            scopes=self.SCOPES,
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
