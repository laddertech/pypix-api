from typing import ClassVar

from pypix_api.banks.base import BankPixAPIBase


class SicrediPixAPI(BankPixAPIBase):
    """Implementação da API PIX do Sicredi.

    Diferentemente de BB e Sicoob, a API Pix do Sicredi usa o prefixo ``/api``
    com **versionamento por recurso**: a cobrança imediata por identificador
    (``/cob/{txid}``) está em ``v3``, os demais recursos do Pix comum
    (``cobv``, ``pix``, ``webhook``, ``loc``, ``lotecobv``) em ``v2`` e todo o
    Pix Automático (``cobr``, ``rec``, ``locrec``, ``solicrec``,
    ``webhookcobr``, ``webhookrec``) em ``v1``. Por isso ``BASE_URL`` aponta
    apenas para a raiz ``/api`` e a versão é injetada em ``_endpoint_url``.

    A autenticação exige mTLS + OAuth2 ``client_credentials`` com
    ``Authorization: Basic base64(client_id:client_secret)``. Passe o
    ``client_secret`` ao construir o :class:`OAuth2Client` para ativar o fluxo
    Basic (ver ``OAuth2Client``).

    Args:
        oauth: Instância configurada de OAuth2Client para autenticação
        sandbox_mode: Se True, usa ambiente de sandbox (default: False)

    Attributes:
        BASE_URL: Raiz da API de produção (sem versão)
        SANDBOX_BASE_URL: Raiz da API de homologação (sem versão)
        TOKEN_URL: URL para obtenção de token OAuth2 (produção)
        SANDBOX_TOKEN_URL: URL para obtenção de token OAuth2 (homologação)

    Note:
        O ``sandbox_mode`` da biblioteca usa token fixo e não faz mTLS. A
        homologação real do Sicredi exige mTLS + OAuth; para testá-la, use
        ``sandbox_mode=False`` com ``token_url=SicrediPixAPI.SANDBOX_TOKEN_URL``
        e o certificado de homologação.
    """

    # Raiz da API (sem versão) — a versão é resolvida por recurso em _endpoint_url.
    BASE_URL = 'https://api-pix.sicredi.com.br/api'
    SANDBOX_BASE_URL = 'https://api-pix-h.sicredi.com.br/api'
    TOKEN_URL = 'https://api-pix.sicredi.com.br/oauth/token'  # noqa: S105
    SANDBOX_TOKEN_URL = 'https://api-pix-h.sicredi.com.br/oauth/token'  # noqa: S105

    # Versão da API por recurso (primeiro segmento do path).
    RESOURCE_VERSIONS: ClassVar[dict[str, str]] = {
        'cob': 'v2',
        'cobv': 'v2',
        'lotecobv': 'v2',
        'loc': 'v2',
        'pix': 'v2',
        'webhook': 'v2',
        'cobr': 'v1',
        'rec': 'v1',
        'locrec': 'v1',
        'solicrec': 'v1',
        'webhookcobr': 'v1',
        'webhookrec': 'v1',
    }

    # Recursos cujas operações "por identificador" (com subpath) usam versão
    # diferente da operação de coleção. Ex.: POST/GET ``/cob`` → v2, mas
    # PUT/PATCH/GET ``/cob/{txid}`` → v3.
    RESOURCE_ITEM_VERSIONS: ClassVar[dict[str, str]] = {
        'cob': 'v3',
    }

    DEFAULT_VERSION = 'v2'

    def get_bank_code(self) -> str:
        return '748'

    def get_base_url(self) -> str:
        """Obtém a raiz da API (sem versão) de acordo com o modo de operação.

        Returns:
            str: Raiz da API (produção ou homologação)
        """
        if self.sandbox_mode:
            return self.SANDBOX_BASE_URL
        return self.BASE_URL

    def _endpoint_url(self, path: str) -> str:
        """Resolve a URL absoluta injetando a versão correta do recurso.

        Args:
            path: Caminho do endpoint relativo à base, iniciado por ``/``
                (ex.: ``/cob/{txid}``).

        Returns:
            str: URL absoluta no formato ``{raiz}/{versão}{path}``.
        """
        segments = path.strip('/').split('/')
        resource = segments[0] if segments else ''
        version = self.RESOURCE_VERSIONS.get(resource, self.DEFAULT_VERSION)
        if len(segments) > 1 and resource in self.RESOURCE_ITEM_VERSIONS:
            version = self.RESOURCE_ITEM_VERSIONS[resource]
        return f'{self.get_base_url()}/{version}{path}'
