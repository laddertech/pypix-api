from abc import ABC
from typing import Any, BinaryIO

import requests

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.methods.cob_methods import CobMethods
from pypix_api.banks.methods.cobv_methods import CobVMethods
from pypix_api.banks.methods.rec_methods import RecMethods
from pypix_api.banks.methods.solic_rec_methods import SolicRecMethods
from pypix_api.banks.exceptions import (
    PixAcessoNegadoException,
    PixRecursoNaoEncontradoException,
    PixErroValidacaoException,
    PixErroServicoIndisponivelException,
    PixErroDesconhecidoException,
)


class BankPixAPIBase(CobVMethods, CobMethods, RecMethods, SolicRecMethods, ABC):
    """Classe base abstrata para clientes Pix de bancos."""

    BASE_URL = None
    TOKEN_URL = None
    SCOPES = None

    def __init__(
        self,
        client_id: str | None = None,
        cert: str | None = None,
        pvk: str | None = None,
        cert_pfx: str | bytes | BinaryIO | None = None,
        pwd_pfx: str | None = None,
        sandbox_mode: bool = False,
    ) -> None:
        if not self.BASE_URL or not self.TOKEN_URL or not self.SCOPES:
            raise ValueError(
                'BASE_URL, TOKEN_URL e SCOPES devem ser definidos na subclasse.'
            )
        self.sandbox_mode = sandbox_mode

        self.oauth = OAuth2Client(
            token_url=self.TOKEN_URL,
            client_id=client_id,
            cert=cert,
            pvk=pvk,
            cert_pfx=cert_pfx,
            pwd_pfx=pwd_pfx,
            sandbox_mode=sandbox_mode,
        )
        self.session = self.oauth.session
        self.client_id = self.oauth.client_id

    def _create_headers(self) -> dict[str, str]:
        """
        Cria os headers necessários para as requisições.
        """
        if self.sandbox_mode:
            import os

            from dotenv import load_dotenv
            load_dotenv()

            token = os.getenv('SANDBOX_TOKEN', 'sandbox-token')
        else:
            token = self.oauth.get_token()

        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'PyPixAPIClient/0.1',
            'client_id': self.client_id or '',
        }

    def _handle_error_response(
        self, response: requests.Response, **kwargs: Any
    ) -> None:
        """Trata respostas de erro da API de forma centralizada

        Args:
            response: Objeto Response da requisição
            **kwargs: Argumentos adicionais para a exceção

        Raises:
            Exceção personalizada baseada no erro retornado pela API Pix
        """
        if response.status_code in (400, 403, 404, 503):
            try:
                error_data = response.json()
            except ValueError:
                error_data = {}

            type_ = error_data.get('type', '')
            title = error_data.get('title', '')
            status = error_data.get('status', response.status_code)
            detail = error_data.get('detail', '')

            # Mapeamento para exceções específicas
            if status == 403 or 'AcessoNegado' in type_:
                raise PixAcessoNegadoException(type_, title, status, detail)
            elif status == 404 or 'RecursoNaoEncontrado' in type_:
                raise PixRecursoNaoEncontradoException(type_, title, status, detail)
            elif status == 400 or 'ErroValidacao' in type_:
                raise PixErroValidacaoException(type_, title, status, detail)
            elif status == 503:
                raise PixErroServicoIndisponivelException(type_, title, status, detail)
            else:
                raise PixErroDesconhecidoException(type_, title, status, detail)

        response.raise_for_status()
