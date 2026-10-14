import re
from typing import Any

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.base import BankPixAPIBase
from pypix_api.banks.methods.pix_inter_methods import PixInterMethods
from pypix_api.http import Timeout
from pypix_api.scopes import ScopeGroup

_CONTA_CORRENTE_VALIDA = re.compile(r'[1-9][0-9]*')


class InterPixAPI(PixInterMethods, BankPixAPIBase):
    """Implementação da API PIX do Banco Inter.

    Uma única versão (``/pix/v2``) cobre o Pix comum e o Pix Automático. A
    autenticação exige mTLS + OAuth2 ``client_credentials`` com ``client_id``
    e ``client_secret`` **no corpo do form** — construa o
    :class:`OAuth2Client` com ``client_secret`` e ``client_auth='body'``.

    Args:
        oauth: Instância configurada de OAuth2Client para autenticação
        sandbox_mode: Se True, usa as URLs do Sandbox com token fixo, sem
            OAuth — útil só para testes locais; o Sandbox do Inter recusa o
            token fixo. Para o Sandbox real, use ``homologacao`` (default: False)
        timeout: Tempo limite das requisições (ver :class:`BankPixAPIBase`)
        scopes: Escopos OAuth2 a solicitar (ver :class:`BankPixAPIBase`)
        conta_corrente: Conta corrente da operação, enviada no header
            ``x-conta-corrente``. Necessária só quando a integração estiver
            associada a mais de uma conta. Apenas números, incluindo o dígito;
            hífen, ponto, espaços e zeros à esquerda são removidos
        homologacao: Se True, usa as URLs do Sandbox do Inter com OAuth e mTLS
            reais — o Sandbox do Inter exige certificado e credenciais da
            integração de testes. Use com
            ``token_url=InterPixAPI.SANDBOX_TOKEN_URL``. Libera os métodos
            ``sandbox_*`` (default: False)

    Attributes:
        BASE_URL: URL da API de produção
        SANDBOX_BASE_URL: URL da API do Sandbox
        TOKEN_URL: URL para obtenção de token OAuth2 (produção)
        SANDBOX_TOKEN_URL: URL para obtenção de token OAuth2 (Sandbox)

    Raises:
        ValueError: Se ``conta_corrente`` não contiver um número válido
    """

    BASE_URL = 'https://cdpj.partners.bancointer.com.br/pix/v2'
    SANDBOX_BASE_URL = 'https://cdpj-sandbox.partners.uatinter.co/pix/v2'
    TOKEN_URL = 'https://cdpj.partners.bancointer.com.br/oauth/v2/token'  # noqa: S105
    SANDBOX_TOKEN_URL = 'https://cdpj-sandbox.partners.uatinter.co/oauth/v2/token'  # noqa: S105

    # A especificação do Inter nomeia o filtro de GET /pix como `txId`.
    PARAM_TXID_CONSULTA_PIX = 'txId'

    conta_corrente: str | None
    homologacao: bool

    def __init__(
        self,
        oauth: OAuth2Client,
        sandbox_mode: bool = False,
        timeout: Timeout | None = None,
        scopes: str | ScopeGroup | list[str | ScopeGroup] | None = None,
        *,
        conta_corrente: str | int | None = None,
        homologacao: bool = False,
    ) -> None:
        super().__init__(oauth, sandbox_mode, timeout, scopes)
        self.conta_corrente = _normaliza_conta_corrente(conta_corrente)
        self.homologacao = homologacao

    def get_bank_code(self) -> str:
        return '077'

    def get_base_url(self) -> str:
        """Obtém a URL base da API de acordo com o modo de operação.

        Returns:
            str: URL base da API (produção ou Sandbox)
        """
        if self._em_sandbox():
            return self.SANDBOX_BASE_URL
        return self.BASE_URL

    def _create_headers(self) -> dict[str, str]:
        """Acrescenta o ``x-conta-corrente`` aos headers padrão, quando houver."""
        headers = super()._create_headers()
        if self.conta_corrente:
            headers['x-conta-corrente'] = self.conta_corrente
        return headers

    def listar_webhooks(
        self, inicio: str, fim: str, pagina_atual: int = 0, itens_por_pagina: int = 100
    ) -> dict[str, Any]:
        """Não suportado: o Inter não oferece ``GET /webhook``.

        Raises:
            NotImplementedError: Sempre. Use ``consultar_webhook(chave)``
        """
        raise NotImplementedError(
            'O Inter não oferece a listagem de webhooks (GET /webhook). '
            'Use consultar_webhook(chave).'
        )

    def _em_sandbox(self) -> bool:
        return self.sandbox_mode or self.homologacao

    def _exige_sandbox(self, metodo: str) -> None:
        """Recusa, antes de pedir token, um endpoint exclusivo do Sandbox
        chamado contra produção."""
        # `sandbox_mode` não basta: usa token fixo, e o Sandbox do Inter exige
        # OAuth e mTLS reais.
        if not self.homologacao:
            raise ValueError(
                f'{metodo} só existe no Sandbox do Inter, que exige OAuth e mTLS. '
                'Construa a InterPixAPI com homologacao=True e o OAuth2Client com '
                'token_url=InterPixAPI.SANDBOX_TOKEN_URL.'
            )

    def _exige_producao(self, metodo: str) -> None:
        """Recusa, antes de pedir token, um endpoint que só existe em
        produção chamado contra o Sandbox."""
        if self._em_sandbox():
            raise ValueError(
                f'{metodo} só existe na produção do Inter. Construa a InterPixAPI '
                'sem homologacao nem sandbox_mode.'
            )


def _normaliza_conta_corrente(conta: str | int | None) -> str | None:
    """Normaliza a conta para o formato do header: só dígitos, sem zero à
    esquerda."""
    if conta is None:
        return None
    normalizada = re.sub(r'[\s.-]', '', str(conta)).lstrip('0')
    if not _CONTA_CORRENTE_VALIDA.fullmatch(normalizada):
        raise ValueError(
            f'conta_corrente inválida: {conta!r}. Informe apenas os números '
            'da conta, incluindo o dígito.'
        )
    return normalizada
