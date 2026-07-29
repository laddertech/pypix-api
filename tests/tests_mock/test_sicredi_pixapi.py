"""Testes mock do Sicredi.

Focam nas particularidades do banco: versionamento por recurso na montagem de
URL (``cob`` por txid em v3, demais recursos do Pix comum em v2, Pix Automático
em v1), código do banco, resolução de escopos e o fluxo de token via HTTP Basic.
"""

import base64
from unittest.mock import MagicMock

import pytest

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.sicredi import SicrediPixAPI
from pypix_api.scopes import ScopeRegistry, get_pix_scopes
from tests.conftest import make_response

SANDBOX_BASE = 'https://api-pix-h.sicredi.com.br/api'


@pytest.fixture
def sicredi_pix_api() -> SicrediPixAPI:
    mock_oauth = MagicMock()
    mock_oauth.session = MagicMock()
    mock_oauth.client_id = 'test-client-id'
    return SicrediPixAPI(oauth=mock_oauth, sandbox_mode=True)


# --- Versionamento por recurso (_endpoint_url) --------------------------------


@pytest.mark.parametrize(
    ('path', 'expected'),
    [
        # cob: coleção em v2, item (por txid) em v3
        ('/cob', f'{SANDBOX_BASE}/v2/cob'),
        ('/cob/txid123', f'{SANDBOX_BASE}/v3/cob/txid123'),
        # demais recursos do Pix comum em v2
        ('/cobv/txid123', f'{SANDBOX_BASE}/v2/cobv/txid123'),
        ('/cobv', f'{SANDBOX_BASE}/v2/cobv'),
        ('/lotecobv/lote1', f'{SANDBOX_BASE}/v2/lotecobv/lote1'),
        ('/pix', f'{SANDBOX_BASE}/v2/pix'),
        ('/pix/E2E/devolucao/1', f'{SANDBOX_BASE}/v2/pix/E2E/devolucao/1'),
        ('/webhook/chave', f'{SANDBOX_BASE}/v2/webhook/chave'),
        ('/loc/1', f'{SANDBOX_BASE}/v2/loc/1'),
        # Pix Automático em v1
        ('/cobr', f'{SANDBOX_BASE}/v1/cobr'),
        ('/cobr/txid', f'{SANDBOX_BASE}/v1/cobr/txid'),
        ('/rec/idRec', f'{SANDBOX_BASE}/v1/rec/idRec'),
        ('/locrec/id', f'{SANDBOX_BASE}/v1/locrec/id'),
        ('/solicrec/id', f'{SANDBOX_BASE}/v1/solicrec/id'),
        ('/webhookcobr', f'{SANDBOX_BASE}/v1/webhookcobr'),
        ('/webhookrec', f'{SANDBOX_BASE}/v1/webhookrec'),
    ],
)
def test_endpoint_url_versionamento(
    sicredi_pix_api: SicrediPixAPI, path: str, expected: str
) -> None:
    assert sicredi_pix_api._endpoint_url(path) == expected


def test_endpoint_url_producao_usa_host_de_producao() -> None:
    mock_oauth = MagicMock()
    mock_oauth.session = MagicMock()
    api = SicrediPixAPI(oauth=mock_oauth, sandbox_mode=False)
    assert (
        api._endpoint_url('/cob/txid')
        == 'https://api-pix.sicredi.com.br/api/v3/cob/txid'
    )
    assert api._endpoint_url('/cobr') == 'https://api-pix.sicredi.com.br/api/v1/cobr'


# --- Integração método ↔ _endpoint_url ----------------------------------------


def test_criar_cob_usa_v3(sicredi_pix_api: SicrediPixAPI) -> None:
    sicredi_pix_api.session.request.return_value = make_response(200, {'txid': 'abc'})
    sicredi_pix_api.criar_cob('abc', {'valor': {'original': '1.00'}})
    args, _ = sicredi_pix_api.session.request.call_args
    assert args[1] == f'{SANDBOX_BASE}/v3/cob/abc'


def test_consultar_cobs_usa_v2(sicredi_pix_api: SicrediPixAPI) -> None:
    sicredi_pix_api.session.request.return_value = make_response(200, {'cobs': []})
    sicredi_pix_api.consultar_cobs(
        inicio='2025-01-01T00:00:00Z', fim='2025-01-31T23:59:59Z'
    )
    args, _ = sicredi_pix_api.session.request.call_args
    assert args[1] == f'{SANDBOX_BASE}/v2/cob'


def test_criar_recorrencia_usa_v1(sicredi_pix_api: SicrediPixAPI) -> None:
    sicredi_pix_api.session.request.return_value = make_response(200, {'idRec': 'RR1'})
    sicredi_pix_api.criar_recorrencia({'vinculo': {}})
    args, _ = sicredi_pix_api.session.request.call_args
    assert args[1] == f'{SANDBOX_BASE}/v1/rec'


# --- Identidade do banco e escopos --------------------------------------------


def test_get_bank_code() -> None:
    mock_oauth = MagicMock()
    mock_oauth.session = MagicMock()
    api = SicrediPixAPI(oauth=mock_oauth, sandbox_mode=True)
    assert api.get_bank_code() == '748'


def test_urls_e_token() -> None:
    assert SicrediPixAPI.BASE_URL == 'https://api-pix.sicredi.com.br/api'
    assert SicrediPixAPI.SANDBOX_BASE_URL == 'https://api-pix-h.sicredi.com.br/api'
    assert SicrediPixAPI.TOKEN_URL == 'https://api-pix.sicredi.com.br/oauth/token'


def test_registry_resolve_sicredi() -> None:
    assert '748' in ScopeRegistry.list_banks()
    assert 'sicredi' in ScopeRegistry.list_banks()
    scopes = get_pix_scopes('748')
    # Deve conter tanto Pix comum quanto Pix Automático
    assert 'cob.write' in scopes
    assert 'cobr.write' in scopes
    assert 'rec.write' in scopes
    assert 'webhookrec.write' in scopes


# --- OAuth2Client: fluxo Basic auth (Sicredi) ---------------------------------


def test_get_token_com_client_secret_usa_basic() -> None:
    client = OAuth2Client(
        token_url='https://api-pix.sicredi.com.br/oauth/token',
        client_id='id',
        client_secret='secret',
        sandbox_mode=True,
    )
    captured: dict = {}

    def fake_post(url: str, data=None, headers=None, timeout=None):  # type: ignore[no-untyped-def]
        captured['data'] = data
        captured['headers'] = headers
        return make_response(200, {'access_token': 'tok', 'expires_in': 3600})

    client.session.post = fake_post  # type: ignore[method-assign]
    token = client.get_token('cob.read')

    expected = base64.b64encode(b'id:secret').decode()
    assert token == 'tok'
    assert captured['headers']['Authorization'] == f'Basic {expected}'
    # No fluxo Basic o client_id não vai no corpo
    assert 'client_id' not in captured['data']
    assert captured['data']['scope'] == 'cob.read'


def test_get_token_sem_client_secret_mantem_fluxo_padrao() -> None:
    client = OAuth2Client(
        token_url='https://oauth.bb.com.br/oauth/token',
        client_id='id',
        sandbox_mode=True,
    )
    captured: dict = {}

    def fake_post(url: str, data=None, headers=None, timeout=None):  # type: ignore[no-untyped-def]
        captured['data'] = data
        captured['headers'] = headers
        return make_response(200, {'access_token': 'tok', 'expires_in': 3600})

    client.session.post = fake_post  # type: ignore[method-assign]
    client.get_token('pix.read')

    # Fluxo inalterado: client_id no corpo, sem header Authorization
    assert captured['data']['client_id'] == 'id'
    assert 'Authorization' not in captured['headers']
