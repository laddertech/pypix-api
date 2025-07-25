from abc import ABC
from typing import Any

import requests

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.exceptions import (
    PixAcessoNegadoException,
    PixErroDesconhecidoException,
    PixErroServicoIndisponivelException,
    PixErroValidacaoException,
    PixRecursoNaoEncontradoException,
)
from pypix_api.banks.methods.cob_methods import CobMethods
from pypix_api.banks.methods.cobv_methods import CobVMethods
from pypix_api.banks.methods.rec_methods import RecMethods
from pypix_api.banks.methods.solic_rec_methods import SolicRecMethods
from pypix_api.banks.methods.webhook_cobr_methods import WebHookCobrMethods
from pypix_api.banks.methods.webhook_methods import WebHookMethods
from pypix_api.banks.methods.webhook_rec_methods import WebHookRecMethods


class BankPixAPIBase(
    CobVMethods,
    CobMethods,
    RecMethods,
    SolicRecMethods,
    WebHookMethods,
    WebHookRecMethods,
    WebHookCobrMethods,
    ABC,
):
    """Classe base abstrata para clientes Pix de bancos.

    Attributes:
        BASE_URL (str): URL base da API do banco (deve ser definido na subclasse)
        TOKEN_URL (str): URL para obtenção de token OAuth2 (deve ser definido na subclasse)
        SCOPES (list): Lista de scopes OAuth2 necessários (deve ser definido na subclasse)
    """

    BASE_URL = None
    TOKEN_URL = None
    SCOPES = None

    def __init__(
        self,
        oauth: OAuth2Client,
        sandbox_mode: bool = False,
    ) -> None:
        """Inicializa o cliente Pix do banco.

        Args:
            oauth: Instância configurada de OAuth2Client para autenticação
            sandbox_mode: Se True, usa modo sandbox com token fixo (default: False)

        Raises:
            ValueError: Se BASE_URL, TOKEN_URL ou SCOPES não forem definidos na subclasse
        """
        if not self.BASE_URL or not self.TOKEN_URL or not self.SCOPES:
            raise ValueError(
                "BASE_URL, TOKEN_URL e SCOPES devem ser definidos na subclasse."
            )
        self.sandbox_mode = sandbox_mode
        self.oauth = oauth
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

            token = os.getenv("SANDBOX_TOKEN", "sandbox-token")
        else:
            token = self.oauth.get_token()

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "PyPixAPIClient/0.1",
            "client_id": self.client_id or "",
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

            type_ = error_data.get("type", "")
            title = error_data.get("title", "")
            status = error_data.get("status", response.status_code)
            detail = error_data.get("detail", "")

            # Mapeamento para exceções específicas
            if status == 403 or "AcessoNegado" in type_:
                raise PixAcessoNegadoException(type_, title, status, detail)
            elif status == 404 or "RecursoNaoEncontrado" in type_:
                raise PixRecursoNaoEncontradoException(type_, title, status, detail)
            elif status == 400 or "ErroValidacao" in type_:
                raise PixErroValidacaoException(type_, title, status, detail)
            elif status == 503:
                raise PixErroServicoIndisponivelException(type_, title, status, detail)
            else:
                raise PixErroDesconhecidoException(type_, title, status, detail)

        response.raise_for_status()
