from pypix_api.banks.base import BankPixAPIBase

class SicoobPixAPI(BankPixAPIBase):
    """Sicoob API client for Pix operations."""

    BASE_URL = "https://api.sicoob.com.br/pix"
    TOKEN_URL = "https://auth.sicoob.com.br/auth/realms/sicoob/protocol/openid-connect/token"
    SCOPES = "cob.read cob.write pix.read pix.write"
