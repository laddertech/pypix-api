from abc import ABC
from typing import Any

import requests

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.methods.cob_methods import CobMethods
from pypix_api.banks.methods.cobr_methods import CobRMethods
from pypix_api.banks.methods.cobv_methods import CobVMethods
from pypix_api.banks.methods.loc_methods import LocMethods
from pypix_api.banks.methods.locrec_methods import LocRecMethods
from pypix_api.banks.methods.lotecobv_methods import LoteCobVMethods
from pypix_api.banks.methods.pix_methods import PixMethods
from pypix_api.banks.methods.rec_methods import RecMethods
from pypix_api.banks.methods.solic_rec_methods import SolicRecMethods
from pypix_api.banks.methods.webhook_cobr_methods import WebHookCobrMethods
from pypix_api.banks.methods.webhook_methods import WebHookMethods
from pypix_api.banks.methods.webhook_rec_methods import WebHookRecMethods
from pypix_api.exceptions import (
    PixAcessoNegadoException,
    PixAPIException,
    PixConexaoException,
    PixErroValidacaoException,
    PixRecursoNaoEncontradoException,
    PixRespostaInvalidaError,
    PixTimeoutException,
    excecao_para_status,
)
from pypix_api.http import DEFAULT_TIMEOUT, Timeout, texto_do_corpo
from pypix_api.scopes import ScopeGroup, get_pix_scopes

#: Headers montados por `_create_headers` que ``extra_headers`` não pode
#: redefinir — trocá-los quebraria a autenticação da requisição.
_HEADERS_PROTEGIDOS = frozenset({'authorization', 'client_id'})


def _e_json(content_type: str) -> bool:
    """Reconhece qualquer subtipo JSON no ``Content-Type``.

    Os corpos de erro da especificação do BACEN vêm em
    ``application/problem+json`` (RFC 7807), não em ``application/json`` — e um
    PSP pode ainda usar um tipo de fornecedor terminado em ``+json``.
    """
    tipo = content_type.split(';', 1)[0].strip().lower()
    return tipo.endswith('/json') or tipo.endswith('+json')


def _para_int(valor: Any, padrao: int) -> int:
    """Converte o ``status`` do corpo para int, tolerando string e ausência."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return padrao


#: Mensagem do `TypeError` de `_normaliza_scopes`, que nomeia o parâmetro — sem
#: ela, o erro chega como um `AttributeError` de `.split()`, sem pista da causa.
_TIPO_SCOPES_INVALIDO = (
    'O parâmetro `scopes` aceita str, ScopeGroup ou uma lista desses tipos; '
    'recebido {tipo}.'
)


def _normaliza_scopes(
    scopes: str | ScopeGroup | list[str | ScopeGroup],
) -> str:
    """Normaliza o parâmetro ``scopes`` para a string enviada ao PSP.

    Aceita as formas naturais de expressar um conjunto de escopos — a string
    crua, um :class:`ScopeGroup`, e a lista de qualquer um dos dois — e devolve
    sempre a string separada por espaços que o ``grant_type=client_credentials``
    espera, sem duplicatas e preservando a ordem informada.

    Args:
        scopes: Escopos a solicitar, como string, :class:`ScopeGroup` ou lista
            de ambos (ex.: ``[SicrediScopes.COB, SicrediScopes.COBR]``)

    Returns:
        str: Escopos separados por espaço

    Raises:
        ValueError: Se a entrada não produzir escopo algum (``''``, ``'   '``,
            ``[]``). Um conjunto vazio não pode virar silenciosamente "todos os
            escopos do banco": quem quer o conjunto completo omite o parâmetro
        TypeError: Se a entrada — ou algum item da lista — não for ``str`` nem
            :class:`ScopeGroup`
    """
    if isinstance(scopes, str | ScopeGroup):
        entradas: list[Any] = [scopes]
    else:
        try:
            entradas = list(scopes)
        except TypeError as exc:
            raise TypeError(
                _TIPO_SCOPES_INVALIDO.format(tipo=type(scopes).__name__)
            ) from exc

    itens: list[str] = []
    for entrada in entradas:
        if isinstance(entrada, ScopeGroup):
            itens.extend(entrada.scopes)
        elif isinstance(entrada, str):
            itens.extend(entrada.split())
        else:
            raise TypeError(_TIPO_SCOPES_INVALIDO.format(tipo=type(entrada).__name__))

    unicos = list(dict.fromkeys(itens))
    if not unicos:
        raise ValueError(
            'O parâmetro `scopes` não pode ser vazio. Informe os escopos '
            'liberados para a credencial (ver `pypix_api.scopes.compose_scopes`) '
            'ou omita o parâmetro para usar o conjunto Pix completo do banco.'
        )
    return ' '.join(unicos)


def _classe_da_excecao(status: int, type_: str) -> type[PixAPIException]:
    """Resolve a exceção de um erro devolvido pelo PSP.

    O campo ``type`` do corpo (padrão do BACEN) tem precedência sobre o status,
    porque descreve a recusa com mais precisão; na ausência dele, vale o
    mapeamento por status de :func:`pypix_api.exceptions.excecao_para_status`.
    """
    if status == 403 or 'AcessoNegado' in type_:
        return PixAcessoNegadoException
    if status == 404 or 'RecursoNaoEncontrado' in type_:
        return PixRecursoNaoEncontradoException
    if status == 400 or 'ErroValidacao' in type_:
        return PixErroValidacaoException
    return excecao_para_status(status)


class BankPixAPIBase(
    CobVMethods,
    CobMethods,
    CobRMethods,
    LoteCobVMethods,
    LocMethods,
    LocRecMethods,
    PixMethods,
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

    BASE_URL: str | None = None
    TOKEN_URL: str | None = None

    # Atributos de instância com type hints
    sandbox_mode: bool
    oauth: OAuth2Client
    session: requests.Session
    client_id: str | None
    timeout: Timeout
    scopes: str | None

    def __init__(
        self,
        oauth: OAuth2Client,
        sandbox_mode: bool = False,
        timeout: Timeout | None = None,
        scopes: str | ScopeGroup | list[str | ScopeGroup] | None = None,
    ) -> None:
        """Inicializa o cliente Pix do banco.

        Args:
            oauth: Instância configurada de OAuth2Client para autenticação
            sandbox_mode: Se True, usa modo sandbox com token fixo (default: False)
            timeout: Tempo limite das requisições, no formato aceito pelo
                ``requests``: um número (aplicado a conexão e leitura) ou a
                tupla ``(conexão, leitura)``. ``None`` usa
                :data:`DEFAULT_TIMEOUT`. Para leitura sem limite, use
                ``(5.0, None)``
            scopes: Escopos OAuth2 a solicitar, como string, :class:`ScopeGroup`
                ou lista de ambos. ``None`` (padrão) mantém o comportamento
                histórico: o grupo Pix completo do banco. Informe este parâmetro
                quando a credencial tiver apenas parte das modalidades
                contratadas junto ao PSP — ver
                :func:`pypix_api.scopes.compose_scopes`

        Raises:
            ValueError: Se BASE_URL ou TOKEN_URL não forem definidos na
                subclasse, ou se ``scopes`` for informado e vazio
            TypeError: Se ``scopes`` não for ``str``, :class:`ScopeGroup` nem
                lista desses tipos
        """
        if not self.BASE_URL or not self.TOKEN_URL:
            raise ValueError(
                'BASE_URL, TOKEN_URL e SCOPES devem ser definidos na subclasse.'
            )
        self.sandbox_mode = sandbox_mode
        self.oauth = oauth
        self.session = self.oauth.session
        self.client_id = self.oauth.client_id
        self.timeout = DEFAULT_TIMEOUT if timeout is None else timeout
        # O agregado do banco continua sendo resolvido em `_create_headers`, e
        # não aqui: um banco fora do ScopeRegistry ou em `sandbox_mode` nunca
        # chega a pedir token, e não deve falhar na construção.
        self.scopes = None if scopes is None else _normaliza_scopes(scopes)

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
            token = self.oauth.get_token(self._scopes_do_token())

        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'PyPixAPIClient/0.1',
            'client_id': self.client_id or '',
        }

    def _scopes_do_token(self) -> str:
        """Escopos a solicitar ao PSP nesta instância.

        Devolve os escopos informados em ``scopes=`` quando houver; do
        contrário, o grupo Pix completo do banco — resolvido aqui, e não na
        construção, para que a instância só dependa do ``ScopeRegistry`` no
        momento em que realmente pede um token.
        """
        if self.scopes is not None:
            return self.scopes
        return get_pix_scopes(self.get_bank_code())

    def get_bank_code(self) -> str:
        raise NotImplementedError('get_bank_code not implemented')

    def _endpoint_url(self, path: str) -> str:
        """Monta a URL absoluta de um endpoint a partir do caminho relativo.

        Por padrão concatena o caminho à URL base única do banco
        (``get_base_url()``), preservando o comportamento histórico. Bancos
        cuja API utilize versionamento por recurso (ex.: Sicredi, com ``cob``
        em v3 e demais recursos em v2/v1) devem sobrescrever este método para
        resolver a versão correta a partir do ``path``.

        Args:
            path: Caminho do endpoint relativo à base, iniciado por ``/``
                (ex.: ``/cob/{txid}``).

        Returns:
            str: URL absoluta do endpoint.
        """
        return f'{self.get_base_url()}{path}'

    def _request(
        self,
        method: str,
        path: str,
        *,
        extra_headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Executa uma requisição à API do banco.

        Ponto único de saída HTTP da biblioteca: garante o timeout, monta os
        headers de autenticação e trata a resposta de erro. Devolve o
        ``Response`` cru — há métodos que dependem do ``status_code`` (204 na
        exclusão de webhook) e não apenas do corpo JSON.

        Args:
            method: Verbo HTTP (``'GET'``, ``'PUT'``, ...)
            path: Caminho relativo à base, iniciado por ``/``
            extra_headers: Headers adicionais. Os headers de autenticação
                (``Authorization`` e ``client_id``) não são sobrescrevíveis:
                informá-los aqui levanta ``ValueError``
            **kwargs: Repassados ao ``requests`` (``json``, ``params``, ...)

        Returns:
            requests.Response: Resposta já validada por
            :meth:`_handle_error_response`

        Raises:
            ValueError: Se ``extra_headers`` tentar redefinir um header de
                autenticação
            PixTimeoutException: Se a requisição exceder o tempo limite
            PixConexaoException: Se houver falha de conexão
            PixAPIException: Para os erros devolvidos pelo PSP
        """
        # Validado antes de `_create_headers`, que pode disparar uma requisição
        # de token: um erro de programação não deve custar um token ao PSP.
        if extra_headers:
            conflitos = sorted(
                chave for chave in extra_headers if chave.lower() in _HEADERS_PROTEGIDOS
            )
            if conflitos:
                raise ValueError(
                    'Headers de autenticação não podem ser redefinidos via '
                    f'extra_headers: {", ".join(conflitos)}'
                )

        headers = self._create_headers()
        if extra_headers:
            headers.update(extra_headers)
        kwargs.setdefault('timeout', self.timeout)

        url = self._endpoint_url(path)
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
        except requests.Timeout as exc:
            raise PixTimeoutException(
                detail=f'{method} {url} excedeu o tempo limite ({self.timeout}): {exc}'
            ) from exc
        except requests.RequestException as exc:
            raise PixConexaoException(detail=f'{method} {url} falhou: {exc}') from exc

        self._handle_error_response(response)
        return response

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
        content_type = response.headers.get('Content-Type', '')
        tem_json = bool(response.content) and _e_json(content_type)

        if response.ok:
            # Sucesso sem corpo é legítimo em vários endpoints da especificação
            # (200 no PUT /webhook, 202 no PUT /lotecobv, 204 nas exclusões).
            # Quem sabe se o corpo é obrigatório é o método que fez a chamada:
            # ver `_json` e `_json_opcional`.
            if not response.content:
                return
            if not tem_json:
                raise PixRespostaInvalidaError(
                    '',
                    'Resposta Inválida',
                    response.status_code,
                    f'Resposta não é JSON (Content-Type: {content_type})',
                )
            return

        # A partir daqui é erro. O corpo pode vir ausente ou fora do padrão do
        # BACEN (HTML de proxy, `null`, lista, formato próprio do gateway) —
        # nesses casos ainda é preciso levantar a exceção do status, e não
        # deixar vazar um erro cru.
        error_data = self._extrai_erro(response) if tem_json else {}

        type_ = str(error_data.get('type') or '')
        status = _para_int(error_data.get('status'), response.status_code)
        title = str(error_data.get('title') or '') or f'Erro HTTP {status}'
        detail = str(error_data.get('detail') or '')
        violacoes = error_data.get('violacoes')
        if not isinstance(violacoes, list):
            violacoes = None

        if not detail and response.content:
            # Corpo sem `detail` reconhecível (formato próprio do gateway, HTML
            # de proxy, texto puro). Preservá-lo é o que o PSP pede para abrir
            # chamado — sem isto, a recusa chega ao consumidor sem motivo algum.
            detail = texto_do_corpo(response)

        raise _classe_da_excecao(status, type_)(type_, title, status, detail, violacoes)

    def _json(self, response: requests.Response) -> dict[str, Any]:
        """Corpo JSON de uma resposta que, pela especificação, deve trazê-lo.

        Raises:
            PixRespostaInvalidaError: Se a resposta vier sem corpo
        """
        if not response.content:
            raise PixRespostaInvalidaError(
                '',
                'Resposta Inválida',
                response.status_code,
                'Resposta sem corpo onde a especificação exige um',
            )
        return response.json()

    def _json_opcional(self, response: requests.Response) -> dict[str, Any]:
        """Corpo JSON de uma resposta que pode vir vazia.

        É o caso dos endpoints que a especificação define sem corpo em caso de
        sucesso: ``PUT``/``PATCH /lotecobv/{id}`` (202) e ``PUT`` de webhook
        (200). Devolve ``{}`` quando não há corpo.
        """
        if not response.content:
            return {}
        return response.json()

    @staticmethod
    def _extrai_erro(response: requests.Response) -> dict[str, Any]:
        """Extrai o corpo de erro, tolerando JSON válido que não seja um objeto.

        ``null`` e listas são JSON válidos e não levantam ``ValueError``; sem
        esta checagem, o acesso aos campos estouraria com ``AttributeError``.
        """
        try:
            dados = response.json()
        except ValueError:
            return {}
        return dados if isinstance(dados, dict) else {}
