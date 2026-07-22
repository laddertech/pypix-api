import base64
import os
import time
from typing import Any, BinaryIO

import requests
from dotenv import load_dotenv

from pypix_api.auth.mtls import get_session_with_mtls


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
        """
        load_dotenv()

        self.client_id: str | None = client_id or os.getenv('CLIENT_ID')
        self.client_secret: str | None = client_secret or os.getenv('CLIENT_SECRET')
        self.cert: str | None = cert or os.getenv('CERT')
        self.pvk: str | None = pvk or os.getenv('PVK')
        self.cert_pfx: str | bytes | BinaryIO | None = cert_pfx or os.getenv('CERT_PFX')
        self.pwd_pfx: str | None = pwd_pfx or os.getenv('PWD_PFX')

        self.token_url: str = token_url  # URL de autenticação OAuth2
        self.token_cache: dict[str, dict[str, Any]] = {}  # Cache de tokens por escopo
        self.session: requests.Session = requests.Session()

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
        if scope in self.token_cache and not self._is_token_expired(scope):
            return self.token_cache[scope]['access_token']

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

        response = self.session.post(self.token_url, data=token_data, headers=headers)
        response.raise_for_status()

        token_info = response.json()
        token_info['expires_at'] = time.time() + token_info['expires_in']

        # Armazena o token no cache por escopo
        self.token_cache[scope] = token_info

        return token_info['access_token']

    def _is_token_expired(self, scope: str) -> bool:
        """Verifica se o token para o escopo especificado expirou"""
        if scope not in self.token_cache or 'expires_at' not in self.token_cache[scope]:
            return True
        return (
            time.time() >= self.token_cache[scope]['expires_at'] - 60
        )  # 60s de margem
