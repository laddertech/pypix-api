"""``token_store`` plugável do ``OAuth2Client``.

Sem store compartilhado, cada instância pede um token novo ao PSP; uma
aplicação que cria um cliente por requisição estoura o limite de emissão
(Sicredi: ``429 Limite de tokens excedido``).
"""

import contextlib
import time
from collections.abc import Iterator
from typing import Any

import pytest

from pypix_api import InMemoryTokenStore, TokenStore
from pypix_api.auth.oauth2 import OAuth2Client
from tests.conftest import make_response

ESCOPO = 'cob.read cob.write'


class ContadorDePost:
    def __init__(self, expires_in: int = 3600) -> None:
        self.chamadas = 0
        self.expires_in = expires_in

    def __call__(self, *args: Any, **kwargs: Any):
        self.chamadas += 1
        return make_response(
            200,
            {
                'access_token': f'token-{self.chamadas}',
                'token_type': 'Bearer',
                'expires_in': self.expires_in,
                'scope': ESCOPO,
            },
        )


def _cliente(
    monkeypatch: pytest.MonkeyPatch,
    post: ContadorDePost,
    store: Any,
    client_id: str = 'client-a',
    client_secret: str | None = None,
    token_url: str = 'https://psp/oauth/token',  # noqa: S107
) -> OAuth2Client:
    monkeypatch.delenv('CLIENT_SECRET', raising=False)
    client = OAuth2Client(
        token_url=token_url,
        client_id=client_id,
        sandbox_mode=True,
        client_secret=client_secret,
        token_store=store,
    )
    client.session.post = post  # type: ignore[method-assign]
    return client


def test_sem_store_cada_instancia_pede_token(monkeypatch: pytest.MonkeyPatch) -> None:
    post = ContadorDePost()

    _cliente(monkeypatch, post, None).get_token(ESCOPO)
    _cliente(monkeypatch, post, None).get_token(ESCOPO)

    assert post.chamadas == 2


def test_store_compartilhado_reaproveita_token_entre_instancias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    post = ContadorDePost()
    store = InMemoryTokenStore()

    primeiro = _cliente(monkeypatch, post, store).get_token(ESCOPO)
    segundo = _cliente(monkeypatch, post, store).get_token('cob.write cob.read')

    assert post.chamadas == 1
    assert primeiro == segundo == 'token-1'


def test_store_isola_credencial_e_psp(monkeypatch: pytest.MonkeyPatch) -> None:
    post = ContadorDePost()
    store = InMemoryTokenStore()

    _cliente(monkeypatch, post, store, client_id='client-a').get_token(ESCOPO)
    _cliente(monkeypatch, post, store, client_id='client-b').get_token(ESCOPO)
    _cliente(
        monkeypatch, post, store, token_url='https://outro-psp/oauth/token'
    ).get_token(ESCOPO)

    assert post.chamadas == 3


def test_chave_do_store_nao_expoe_client_id(monkeypatch: pytest.MonkeyPatch) -> None:
    store = InMemoryTokenStore()

    _cliente(monkeypatch, ContadorDePost(), store, client_id='segredo-id').get_token(
        ESCOPO
    )

    (chave,) = store._dados
    assert chave.startswith('pypix_api:token:')
    assert 'segredo-id' not in chave


def test_token_vencido_no_store_e_renovado(monkeypatch: pytest.MonkeyPatch) -> None:
    post = ContadorDePost()
    store = InMemoryTokenStore()
    cliente = _cliente(monkeypatch, post, store)
    cliente.get_token(ESCOPO)
    (chave,) = store._dados
    store._dados[chave]['expires_at'] = time.time() + 30  # dentro da margem

    _cliente(monkeypatch, post, store).get_token(ESCOPO)

    assert post.chamadas == 2


def test_ttl_gravado_desconta_a_margem(monkeypatch: pytest.MonkeyPatch) -> None:
    gravados: list[int] = []

    class Store:
        def get(self, key: str) -> None:
            return None

        def set(self, key: str, value: dict[str, Any], ttl: int) -> None:
            gravados.append(ttl)

    _cliente(monkeypatch, ContadorDePost(expires_in=300), Store()).get_token(ESCOPO)

    assert len(gravados) == 1
    assert 230 <= gravados[0] <= 240


def test_token_curto_demais_nao_e_gravado(monkeypatch: pytest.MonkeyPatch) -> None:
    store = InMemoryTokenStore()

    _cliente(monkeypatch, ContadorDePost(expires_in=30), store).get_token(ESCOPO)

    assert store._dados == {}


@pytest.mark.parametrize(
    'conteudo',
    [
        None,
        'texto',
        {},
        {'access_token': 'x'},
        {'expires_at': 9e12},
        {'access_token': 123, 'expires_at': 9e12},
        {'access_token': 'x', 'expires_at': float('nan')},
        {'access_token': 'x', 'expires_at': float('inf')},
        {'access_token': 'x', 'expires_at': True},
    ],
)
def test_conteudo_invalido_no_store_e_ignorado(
    monkeypatch: pytest.MonkeyPatch, conteudo: Any
) -> None:
    post = ContadorDePost()

    class Store:
        def get(self, key: str) -> Any:
            return conteudo

        def set(self, key: str, value: dict[str, Any], ttl: int) -> None:
            pass

    token = _cliente(monkeypatch, post, Store()).get_token(ESCOPO)

    assert post.chamadas == 1
    assert token == 'token-1'


def test_falha_do_store_nao_impede_o_token(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    class StoreQuebrado:
        def get(self, key: str) -> None:
            raise ConnectionError('redis fora')

        def set(self, key: str, value: dict[str, Any], ttl: int) -> None:
            raise ConnectionError('redis fora')

    post = ContadorDePost()

    token = _cliente(monkeypatch, post, StoreQuebrado()).get_token(ESCOPO)

    assert token == 'token-1'
    assert 'token_store' in caplog.text


def test_store_satisfaz_o_protocolo() -> None:
    assert isinstance(InMemoryTokenStore(), TokenStore)


def test_store_isola_segredo_da_credencial(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mesmo client_id com outro segredo é outra identidade: não pode receber
    o token da primeira."""
    post = ContadorDePost()
    store = InMemoryTokenStore()

    _cliente(monkeypatch, post, store, client_secret='segredo-1').get_token(ESCOPO)
    _cliente(monkeypatch, post, store, client_secret='segredo-2').get_token(ESCOPO)

    assert post.chamadas == 2
    assert all('segredo' not in chave for chave in store._dados)


def test_trava_do_store_serializa_e_rele_o_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Com trava, quem entra depois de outra instância renovar relê o token
    gravado em vez de pedir outro ao PSP."""
    eventos: list[str] = []

    class StoreComTrava(InMemoryTokenStore):
        @contextlib.contextmanager
        def lock(self, key: str) -> Iterator[None]:
            eventos.append('lock')
            # Outra instância renovou enquanto esta esperava a trava.
            self.set(
                key.removesuffix(':lock'),
                {
                    'access_token': 'renovado-por-outro',
                    'expires_at': time.time() + 3600,
                },
                3000,
            )
            yield
            eventos.append('unlock')

    post = ContadorDePost()
    token = _cliente(monkeypatch, post, StoreComTrava()).get_token(ESCOPO)

    assert eventos == ['lock', 'unlock']
    assert token == 'renovado-por-outro'
    assert post.chamadas == 0


def test_falha_da_trava_nao_impede_o_token(monkeypatch: pytest.MonkeyPatch) -> None:
    class StoreTravaQuebrada(InMemoryTokenStore):
        def lock(self, key: str) -> Any:
            raise ConnectionError('redis fora')

    post = ContadorDePost()

    token = _cliente(monkeypatch, post, StoreTravaQuebrada()).get_token(ESCOPO)

    assert token == 'token-1'
    assert post.chamadas == 1


def test_rotacao_de_certificado_no_mesmo_caminho_muda_a_chave(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    caminho = tmp_path / 'cert.pem'
    caminho.write_bytes(b'certificado-antigo')
    cliente = _cliente(monkeypatch, ContadorDePost(), InMemoryTokenStore())
    cliente.cert = str(caminho)
    antes = cliente._chave_do_store('cob.read cob.write')

    caminho.write_bytes(b'certificado-novo')

    assert cliente._chave_do_store('cob.read cob.write') != antes


def test_rotacao_durante_a_emissao_nao_grava_token_na_chave_nova(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    caminho = tmp_path / 'cert.pem'
    caminho.write_bytes(b'certificado-antigo')
    store = InMemoryTokenStore()

    class PostQueRotaciona(ContadorDePost):
        def __call__(self, *args: Any, **kwargs: Any):
            caminho.write_bytes(b'certificado-novo')
            return super().__call__(*args, **kwargs)

    cliente = _cliente(monkeypatch, PostQueRotaciona(), store)
    cliente.cert = str(caminho)

    assert cliente.get_token(ESCOPO) == 'token-1'
    assert store._dados == {}
