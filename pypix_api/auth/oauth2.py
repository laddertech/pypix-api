import base64
import logging
import os
import time
from typing import Any, BinaryIO

import requests
from dotenv import load_dotenv

from pypix_api.auth.mtls import get_session_with_mtls
from pypix_api.exceptions import (
    PixAPIException,
    PixConexaoException,
    PixRespostaInvalidaError,
    PixTimeoutException,
    excecao_para_status,
)
from pypix_api.http import DEFAULT_TIMEOUT, Timeout, texto_do_corpo

logger = logging.getLogger(__name__)

#: Máximo de escopos listados no aviso de escopo negado. O campo ``scope`` da
#: resposta é controlado pelo PSP e não tem limite de tamanho; sem o corte, uma
#: resposta inesperada vira uma linha de log de tamanho arbitrário.
_MAX_ESCOPOS_NO_AVISO = 20


class OAuth2Client:
    """Cliente OAuth2 para autenticação com a API"""

    def __init__(
        self,
        token_url: str,
        client_id: str | None = None,
        cert: str | None = None,
        pvk: str | None = None,
        cert_pfx: str | bytes | BinaryIO | None = None,
        pwd_pfx: str | None = None,
        sandbox_mode: bool = False,
        client_secret: str | None = None,
        timeout: Timeout | None = None,
    ) -> None:
        """Inicializa o cliente OAuth2

        Args:
            token_url: URL de autenticação OAuth2
            client_id: Client ID para autenticação OAuth2
            cert: Path para o certificado PEM (opcional)
            pvk: Path para a chave privada PEM (opcional)
            cert_pfx: Path ou dados do certificado PFX (opcional)
            pwd_pfx: Senha do certificado PFX (opcional)
            sandbox_mode: Se True, não requer certificado (default: False)
            client_secret: Client Secret para autenticação via HTTP Basic
                (opcional). Quando informado, o token é solicitado com o header
                ``Authorization: Basic base64(client_id:client_secret)``, como
                exigido por PSPs como o Sicredi. Quando omitido, mantém o fluxo
                padrão (client_id no corpo, autenticação de cliente via mTLS).
                Mantido como último parâmetro para preservar a ordem posicional
                histórica da assinatura.
            timeout: Tempo limite da requisição de token, no formato aceito pelo
                ``requests``: um número ou a tupla ``(conexão, leitura)``.
                ``None`` usa :data:`DEFAULT_TIMEOUT`. Para leitura sem limite,
                use ``(5.0, None)``.
        """
        load_dotenv()

        self.client_id: str | None = client_id or os.getenv('CLIENT_ID')
        self.client_secret: str | None = client_secret or os.getenv('CLIENT_SECRET')
        self.cert: str | None = cert or os.getenv('CERT')
        self.pvk: str | None = pvk or os.getenv('PVK')
        self.cert_pfx: str | bytes | BinaryIO | None = cert_pfx or os.getenv('CERT_PFX')
        self.pwd_pfx: str | None = pwd_pfx or os.getenv('PWD_PFX')

        self.token_url: str = token_url  # URL de autenticação OAuth2
        # Cache de tokens por conjunto de escopos. A chave é a forma canônica
        # (ver `_chave_de_cache`), e não a string solicitada: é detalhe interno,
        # sem garantia de estabilidade entre versões. Para saber se há token
        # válido para um escopo, use `_is_token_expired`, que canoniza a entrada.
        self.token_cache: dict[str, dict[str, Any]] = {}
        self.session: requests.Session = requests.Session()
        self.timeout: Timeout = DEFAULT_TIMEOUT if timeout is None else timeout

        self.sandbox_mode = sandbox_mode

        if not self.sandbox_mode:
            self.session = get_session_with_mtls(
                cert=self.cert,
                pvk=self.pvk,
                cert_pfx=self.cert_pfx,
                pwd_pfx=self.pwd_pfx,
                sandbox_mode=self.sandbox_mode,
            )

    def get_token(self, scope: str | None = None) -> str:
        """Obtém ou renova o token de acesso para o escopo especificado

        Args:
            scope: Escopo(s) necessário(s) para a API. Exemplos:
                - Cobrança por Boleto: "boletos_inclusao boletos_consulta boletos_alteracao webhooks_alteracao webhooks_consulta webhooks_inclusao"
                - Conta Corrente: "cco_consulta cco_transferencias openid"
                - Recebimento no PIX: "cob.write cob.read cobv.write cobv.read lotecobv.write lotecobv.read pix.write pix.read webhook.read webhook.write payloadlocation.write payloadlocation.read"

        Returns:
            str: Token de acesso válido para o escopo solicitado
        """
        # Usa escopo padrão se não especificado (para compatibilidade)
        if scope is None:
            scope = 'cco_extrato cco_consulta'

        # Verifica se já existe token válido para este escopo
        chave = self._chave_de_cache(scope)
        if chave in self.token_cache and not self._is_token_expired(chave):
            return self.token_cache[chave]['access_token']

        token_data: dict[str, str | None] = {
            'grant_type': 'client_credentials',
            'scope': scope,
        }
        headers: dict[str, str] = {}

        if self.client_secret:
            # Autenticação de cliente via HTTP Basic (ex.: Sicredi).
            # O client_id vai no header Basic, não no corpo.
            credentials = base64.b64encode(
                f'{self.client_id}:{self.client_secret}'.encode()
            ).decode()
            headers['Authorization'] = f'Basic {credentials}'
        else:
            # Fluxo padrão (BB, Sicoob): client_id no corpo, cliente
            # autenticado via mTLS. Comportamento inalterado.
            token_data['client_id'] = self.client_id

        try:
            response = self.session.post(
                self.token_url,
                data=token_data,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.Timeout as exc:
            raise PixTimeoutException(
                detail=f'Requisição de token excedeu o tempo limite '
                f'({self.timeout}): {exc}'
            ) from exc
        except requests.RequestException as exc:
            raise PixConexaoException(
                detail=f'Falha ao solicitar token em {self.token_url}: {exc}'
            ) from exc

        if not response.ok:
            raise self._erro_do_token(response)

        token_info = self._le_token(response)
        self._avisa_escopos_ausentes(scope, token_info.get('scope'))
        token_info['expires_at'] = time.time() + token_info['expires_in']

        # Armazena o token no cache por escopo
        self.token_cache[chave] = token_info

        return token_info['access_token']

    @staticmethod
    def _chave_de_cache(scope: str) -> str:
        """Chave canônica do cache para um conjunto de escopos.

        O PSP concede o mesmo token para os mesmos escopos, independentemente da
        ordem e de repetições. Sem canonizar, ``'cob.read cob.write'`` e
        ``'cob.write cob.read'`` seriam entradas distintas e cada uma custaria um
        ``POST /oauth/token`` — o Guia Técnico do Sicredi (§11) associa volume de
        requisições de token a bloqueio por IP. A ordem original é preservada no
        que se envia ao PSP; só a chave do cache é normalizada.
        """
        return ' '.join(sorted(set(scope.split())))

    def _avisa_escopos_ausentes(self, solicitado: str, concedido: Any) -> None:
        """Alerta quando o PSP concede menos escopos do que os solicitados.

        Um PSP pode responder ``200`` devolvendo apenas o subconjunto de
        escopos liberado para a credencial, em vez de recusar o token. Sem este
        aviso, a informação é descartada e a falta só aparece como ``403`` no
        endpoint de negócio, longe da causa — que é a modalidade não contratada.

        Só compara quando a resposta traz o campo ``scope``: a RFC 6749 o torna
        opcional quando o concedido é idêntico ao solicitado.

        Args:
            solicitado: Escopos enviados na requisição de token
            concedido: Campo ``scope`` da resposta, quando presente
        """
        if not isinstance(concedido, str):
            return

        recebidos = set(concedido.split())
        ausentes = [escopo for escopo in solicitado.split() if escopo not in recebidos]
        if not ausentes:
            return

        logger.warning(
            'O PSP concedeu menos escopos do que os solicitados em %s. '
            'Ausentes: %s. Concedidos: %s. Verifique as modalidades '
            'contratadas para esta credencial e ajuste o parâmetro `scopes`.',
            self.token_url,
            self._resume_escopos(ausentes),
            self._resume_escopos(concedido.split()),
        )

    @staticmethod
    def _resume_escopos(escopos: list[str]) -> str:
        """Formata uma lista de escopos para o log, limitando o tamanho.

        Ver :data:`_MAX_ESCOPOS_NO_AVISO`: o excedente vira uma contagem, para
        que a linha de log não cresça sem limite.
        """
        if len(escopos) <= _MAX_ESCOPOS_NO_AVISO:
            return ' '.join(escopos)
        restantes = len(escopos) - _MAX_ESCOPOS_NO_AVISO
        return f'{" ".join(escopos[:_MAX_ESCOPOS_NO_AVISO])} (+{restantes})'

    @staticmethod
    def _corpo_json(response: requests.Response) -> dict[str, Any]:
        """Devolve o corpo JSON quando for um objeto; caso contrário, ``{}``."""
        try:
            dados = response.json()
        except ValueError:
            return {}
        return dados if isinstance(dados, dict) else {}

    def _erro_do_token(self, response: requests.Response) -> PixAPIException:
        """Converte um erro do endpoint de token para a hierarquia da biblioteca.

        O corpo segue a RFC 6749 (``error``/``error_description``), não o
        ``problem+json`` do BACEN — por isso o tratamento é próprio, e não o
        ``_handle_error_response`` dos bancos.
        """
        dados = self._corpo_json(response)
        erro = str(dados.get('error') or '')
        descricao = str(dados.get('error_description') or '')
        detail = ': '.join(parte for parte in (erro, descricao) if parte)
        if not detail and response.content:
            detail = texto_do_corpo(response)

        return excecao_para_status(response.status_code)(
            type_=erro,
            title=f'Falha ao obter token em {self.token_url}',
            status=response.status_code,
            detail=detail,
        )

    def _le_token(self, response: requests.Response) -> dict[str, Any]:
        """Valida o corpo da resposta de token.

        Sem isto, um 200 com corpo vazio ou sem ``access_token`` estouraria com
        ``JSONDecodeError``/``KeyError`` no meio da chamada de negócio.
        """
        dados = self._corpo_json(response)
        if not isinstance(dados.get('access_token'), str) or not dados['access_token']:
            raise PixRespostaInvalidaError(
                '',
                'Resposta de token inválida',
                response.status_code,
                f'`access_token` ausente ou inválido na resposta de {self.token_url}',
            )
        try:
            # `expires_in` pode vir como string; sem converter, a soma com
            # time.time() estoura TypeError fora da hierarquia da biblioteca.
            dados['expires_in'] = int(dados['expires_in'])
        except (KeyError, TypeError, ValueError) as exc:
            raise PixRespostaInvalidaError(
                '',
                'Resposta de token inválida',
                response.status_code,
                f'`expires_in` ausente ou não numérico na resposta de '
                f'{self.token_url}: {dados.get("expires_in")!r}',
            ) from exc
        return dados

    def _is_token_expired(self, scope: str) -> bool:
        """Verifica se o token para o escopo especificado expirou.

        Aceita tanto a string de escopos crua quanto a chave já canônica de
        :meth:`_chave_de_cache` — a canonização é idempotente.
        """
        chave = self._chave_de_cache(scope)
        if chave not in self.token_cache or 'expires_at' not in self.token_cache[chave]:
            return True
        return (
            time.time() >= self.token_cache[chave]['expires_at'] - 60
        )  # 60s de margem
