from pypix_api.banks.base import BankPixAPIBase


class BBPixAPI(BankPixAPIBase):
    """Banco do Brasil API client for Pix operations."""

    BASE_URL = "https://api.bb.com.br/pix/v1"
    SANDBOX_BASE_URL = "https://api.sandbox.bb.com.br/pix/v1"
    TOKEN_URL = "https://oauth.bb.com.br/oauth/token"
    SCOPES = "pix.read pix.write"

    def get_base_url(self) -> str:
        """
        Retorna a URL base da API, diferenciando entre produção e sandbox.
        """
        if self.sandbox_mode:
            return self.SANDBOX_BASE_URL
        return self.BASE_URL
