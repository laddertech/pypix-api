from pypix_api.banks.base import BankPixAPIBase


class BBPixAPI(BankPixAPIBase):
    """Banco do Brasil API client for Pix operations."""

    BASE_URL = 'https://api.bb.com.br/pix/v1'
    TOKEN_URL = 'https://oauth.bb.com.br/oauth/token'
    SCOPES = 'pix.read pix.write'
