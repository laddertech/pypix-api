"""Protocol base para os métodos mixins do PIX API."""

from typing import Any, Protocol

import requests

from pypix_api.http import Timeout


class PixAPIProtocol(Protocol):
    """Protocol que define a interface esperada pelos métodos mixins."""

    session: requests.Session
    client_id: str | None
    sandbox_mode: bool
    oauth: Any  # OAuth2Client
    timeout: Timeout

    def _create_headers(self) -> dict[str, str]:
        """Cria os headers necessários para as requisições."""
        ...

    def _request(
        self,
        method: str,
        path: str,
        *,
        extra_headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Executa uma requisição à API do banco, com timeout e tratamento de erro."""
        ...

    def _json(self, response: requests.Response) -> dict[str, Any]:
        """Corpo JSON de uma resposta que deve trazê-lo."""
        ...

    def _json_opcional(self, response: requests.Response) -> dict[str, Any]:
        """Corpo JSON de uma resposta que pode vir vazia."""
        ...

    def get_base_url(self) -> str:
        """Obtém a URL base da API."""
        ...

    def _endpoint_url(self, path: str) -> str:
        """Monta a URL absoluta de um endpoint a partir do caminho relativo."""
        ...

    def get_bank_code(self) -> str:
        """Obtém o código do banco."""
        ...

    def _handle_error_response(
        self, response: requests.Response, **kwargs: Any
    ) -> None:
        """Trata respostas de erro da API."""
        ...
