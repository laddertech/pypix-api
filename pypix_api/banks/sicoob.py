from pypix_api.banks.base import BankPixAPIBase


class SicoobPixAPI(BankPixAPIBase):
    """Sicoob API client for Pix operations."""

    BASE_URL = 'https://api.sicoob.com.br/pix/api/v2'
    SANDBOX_BASE_URL = 'https://sandbox.sicoob.com.br/sicoob/sandbox/pix/api/v2'
    TOKEN_URL = (
        'https://auth.sicoob.com.br/auth/realms/sicoob/protocol/openid-connect/token'  # noqa: S105
    )
    SCOPES = 'cob.read cob.write pix.read pix.write'

    def get_base_url(self) -> str:
        """
        Retorna a URL base da API, diferenciando entre produção e sandbox.
        """
        if self.sandbox_mode:
            return self.SANDBOX_BASE_URL
        return self.BASE_URL
