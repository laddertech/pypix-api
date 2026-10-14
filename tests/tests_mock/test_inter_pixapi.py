"""Testes mock do Banco Inter.

Focam nas particularidades do banco: URLs de produção e Sandbox (inclusive o
modo ``homologacao``), header ``x-conta-corrente``, escopos, fluxo de token com
credenciais no corpo e os endpoints exclusivos de ``PixInterMethods``.
"""

from decimal import Decimal
from unittest.mock import MagicMock, Mock

import pytest

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.inter import InterPixAPI
from pypix_api.scopes import ScopeRegistry, get_pix_scopes
from tests.conftest import assert_requisicao, make_response

PROD_BASE = 'https://cdpj.partners.bancointer.com.br/pix/v2'
SANDBOX_BASE = 'https://cdpj-sandbox.partners.uatinter.co/pix/v2'


def _oauth() -> MagicMock:
    mock_oauth = MagicMock()
    mock_oauth.session = MagicMock()
    mock_oauth.client_id = 'test-client-id'
    mock_oauth.get_token.return_value = 'tok'
    return mock_oauth


@pytest.fixture
def inter() -> InterPixAPI:
    return InterPixAPI(oauth=_oauth(), homologacao=True)


@pytest.fixture
def inter_prod() -> InterPixAPI:
    return InterPixAPI(oauth=_oauth())


# --- URLs e identidade do banco -----------------------------------------------


def test_urls_e_token() -> None:
    assert InterPixAPI.BASE_URL == PROD_BASE
    assert InterPixAPI.SANDBOX_BASE_URL == SANDBOX_BASE
    assert (
        InterPixAPI.TOKEN_URL
        == 'https://cdpj.partners.bancointer.com.br/oauth/v2/token'
    )
    assert (
        InterPixAPI.SANDBOX_TOKEN_URL
        == 'https://cdpj-sandbox.partners.uatinter.co/oauth/v2/token'
    )


def test_get_bank_code(inter: InterPixAPI) -> None:
    assert inter.get_bank_code() == '077'


@pytest.mark.parametrize(
    ('kwargs', 'esperado'),
    [
        ({}, PROD_BASE),
        ({'sandbox_mode': True}, SANDBOX_BASE),
        ({'homologacao': True}, SANDBOX_BASE),
    ],
)
def test_base_url_por_modo(kwargs: dict, esperado: str) -> None:
    assert InterPixAPI(oauth=_oauth(), **kwargs).get_base_url() == esperado


def test_homologacao_usa_oauth_real(inter: InterPixAPI) -> None:
    inter.session.request.return_value = make_response(200, {'txid': 'abc'})
    inter.consultar_cob('abc')
    inter.oauth.get_token.assert_called_once()
    _, kwargs = inter.session.request.call_args
    assert kwargs['headers']['Authorization'] == 'Bearer tok'


def test_metodo_padrao_usa_url_do_inter(inter_prod: InterPixAPI) -> None:
    inter_prod.session.request.return_value = make_response(200, {'txid': 'abc'})
    inter_prod.criar_cob('abc', {'valor': {'original': '1.00'}})
    args, _ = inter_prod.session.request.call_args
    assert args[1] == f'{PROD_BASE}/cob/abc'


def test_consultar_pix_usa_txId(inter_prod: InterPixAPI) -> None:
    inter_prod.session.request.return_value = make_response(200, {'pix': []})
    inter_prod.consultar_pix('ini', 'fim', txid='abc')
    _, kwargs = inter_prod.session.request.call_args
    assert kwargs['params'] == {'inicio': 'ini', 'fim': 'fim', 'txId': 'abc'}


def test_consultar_cobv_sem_revisao(inter_prod: InterPixAPI) -> None:
    inter_prod.session.request.return_value = make_response(200, {'txid': 'abc'})
    inter_prod.consultar_cobv('abc')
    _, kwargs = inter_prod.session.request.call_args
    assert kwargs['params'] == {}


def test_listar_locations_rec_com_convenio(inter_prod: InterPixAPI) -> None:
    inter_prod.session.request.return_value = make_response(200, {'loc': []})
    inter_prod.listar_locations_rec('ini', 'fim', convenio='123')
    _, kwargs = inter_prod.session.request.call_args
    assert kwargs['params'] == {'inicio': 'ini', 'fim': 'fim', 'convenio': '123'}


def test_listar_webhooks_nao_suportado(inter_prod: InterPixAPI) -> None:
    with pytest.raises(NotImplementedError, match='consultar_webhook'):
        inter_prod.listar_webhooks('ini', 'fim')
    inter_prod.session.request.assert_not_called()


# --- x-conta-corrente -----------------------------------------------------------


def test_sem_conta_corrente_nao_envia_header(inter: InterPixAPI) -> None:
    assert 'x-conta-corrente' not in inter._create_headers()


@pytest.mark.parametrize(
    ('entrada', 'esperado'),
    [
        ('12345678', '12345678'),
        (12345678, '12345678'),
        ('001234567-8', '12345678'),
        (' 1.234.567-8 ', '12345678'),
    ],
)
def test_conta_corrente_normalizada_no_header(entrada: object, esperado: str) -> None:
    api = InterPixAPI(oauth=_oauth(), homologacao=True, conta_corrente=entrada)  # type: ignore[arg-type]
    assert api._create_headers()['x-conta-corrente'] == esperado


@pytest.mark.parametrize('entrada', ['', '000', 'abc', '12a3', 0])
def test_conta_corrente_invalida(entrada: object) -> None:
    with pytest.raises(ValueError, match='conta_corrente'):
        InterPixAPI(oauth=_oauth(), conta_corrente=entrada)  # type: ignore[arg-type]


# --- Escopos ----------------------------------------------------------------------


@pytest.mark.parametrize('codigo', ['077', 'inter', 'banco_inter'])
def test_registry_resolve_inter(codigo: str) -> None:
    assert codigo in ScopeRegistry.list_banks()
    scopes = get_pix_scopes(codigo)
    for escopo in (
        'cob.write',
        'pix.write',
        'cobr.write',
        'solicrec.write',
        'payloadlocationrec.read',
        'payloadlocationrec.write',
    ):
        assert escopo in scopes


# --- OAuth2Client: credenciais no corpo (Inter) ------------------------------------


def _captura_post(client: OAuth2Client) -> dict:
    captured: dict = {}

    def fake_post(url: str, data=None, headers=None, timeout=None, **kwargs):  # type: ignore[no-untyped-def]
        captured['data'] = data
        captured['headers'] = headers
        captured['kwargs'] = kwargs
        return make_response(200, {'access_token': 'tok', 'expires_in': 3600})

    client.session.post = fake_post  # type: ignore[method-assign]
    return captured


def test_get_token_client_auth_body_envia_credenciais_no_corpo() -> None:
    client = OAuth2Client(
        token_url=InterPixAPI.TOKEN_URL,
        client_id='id',
        client_secret='secret',
        sandbox_mode=True,
        client_auth='body',
    )
    captured = _captura_post(client)
    assert client.get_token('cob.read') == 'tok'

    assert captured['data']['client_id'] == 'id'
    assert captured['data']['client_secret'] == 'secret'
    assert captured['data']['grant_type'] == 'client_credentials'
    assert 'Authorization' not in captured['headers']
    # O segredo no corpo não pode seguir um redirecionamento
    assert captured['kwargs'] == {'allow_redirects': False}


def test_client_auth_invalido() -> None:
    with pytest.raises(ValueError, match='client_auth'):
        OAuth2Client(token_url='https://x', sandbox_mode=True, client_auth='form')


# --- Callbacks de webhook ----------------------------------------------------------


def test_consultar_callbacks_webhook(inter_prod: InterPixAPI) -> None:
    inter_prod.session.request.return_value = make_response(200, {'data': []})
    inter_prod.consultar_callbacks_webhook(
        '2025-01-01T00:00:00Z',
        '2025-01-31T23:59:59Z',
        pagina=1,
        tamanho_pagina=50,
        txid='abc',
    )
    assert_requisicao(
        inter_prod.session,
        'GET',
        f'{PROD_BASE}/webhook/callbacks',
        params={
            'dataHoraInicio': '2025-01-01T00:00:00Z',
            'dataHoraFim': '2025-01-31T23:59:59Z',
            'pagina': 1,
            'tamanhoPagina': 50,
            'txid': 'abc',
        },
    )


def test_consultar_callbacks_omite_opcionais(inter_prod: InterPixAPI) -> None:
    inter_prod.session.request.return_value = make_response(200, {'data': []})
    inter_prod.consultar_callbacks_webhook('ini', 'fim')
    _, kwargs = inter_prod.session.request.call_args
    assert kwargs['params'] == {'dataHoraInicio': 'ini', 'dataHoraFim': 'fim'}


def test_reenviar_callbacks_webhook(inter_prod: InterPixAPI) -> None:
    inter_prod.session.request.return_value = make_response(200)
    assert inter_prod.reenviar_callbacks_webhook(['t1', 't2'], 'chave') == {}
    assert_requisicao(
        inter_prod.session,
        'POST',
        f'{PROD_BASE}/webhook/callbacks/retry',
        json={'txId': ['t1', 't2'], 'chavePix': 'chave'},
    )


def test_reenviar_callbacks_aceita_txid_avulso(inter_prod: InterPixAPI) -> None:
    inter_prod.session.request.return_value = make_response(200)
    inter_prod.reenviar_callbacks_webhook('t1', 'chave')
    _, kwargs = inter_prod.session.request.call_args
    assert kwargs['json']['txId'] == ['t1']


@pytest.mark.parametrize('kwargs', [{'homologacao': True}, {'sandbox_mode': True}])
def test_reenviar_callbacks_recusado_no_sandbox(kwargs: dict) -> None:
    api = InterPixAPI(oauth=_oauth(), **kwargs)
    with pytest.raises(ValueError, match='produção'):
        api.reenviar_callbacks_webhook(['t1'], 'chave')
    api.oauth.get_token.assert_not_called()
    api.session.request.assert_not_called()


@pytest.mark.parametrize('txids', [[], [f't{i}' for i in range(51)]])
def test_reenviar_callbacks_limites(inter_prod: InterPixAPI, txids: list) -> None:
    with pytest.raises(ValueError):
        inter_prod.reenviar_callbacks_webhook(txids, 'chave')
    inter_prod.session.request.assert_not_called()


# --- Simulações do Sandbox -----------------------------------------------------------


@pytest.mark.parametrize(
    ('chamada', 'metodo', 'path', 'body'),
    [
        (
            lambda api: api.sandbox_pagar_cob('tx1', Decimal('10.50')),
            'POST',
            '/cob/pagar/tx1',
            {'valor': 10.5},
        ),
        (
            lambda api: api.sandbox_pagar_cobv('tx1', 7),
            'POST',
            '/cobv/pagar/tx1',
            {'valor': 7.0},
        ),
        (
            lambda api: api.sandbox_pagar_qrcode('000201...', 100),
            'POST',
            '/sandbox/cob/pagamento',
            {'qrCode': '000201...', 'valor': 100.0},
        ),
        (
            lambda api: api.sandbox_pagar_cobr('tx1', 1, '12345678909', 'chave'),
            'POST',
            '/sandbox/cobr/pagamento',
            {'valor': 1.0, 'cpfCnpj': '12345678909', 'txId': 'tx1', 'chave': 'chave'},
        ),
        (
            lambda api: api.sandbox_alterar_status_rec('RR1', 'APROVADA'),
            'PATCH',
            '/sandbox/rec/RR1/status',
            {'status': 'APROVADA'},
        ),
        (
            lambda api: api.sandbox_alterar_status_rec('RR1', 'CANCELADA', 'SLDB'),
            'PATCH',
            '/sandbox/rec/RR1/status',
            {'status': 'CANCELADA', 'razao': 'SLDB'},
        ),
        (
            lambda api: api.sandbox_alterar_status_solicrec('RR1', 'ACEITA'),
            'PATCH',
            '/sandbox/solicrec/RR1/status',
            {'status': 'ACEITA'},
        ),
        (
            lambda api: api.sandbox_cancelar_cobr('tx1', 'OTHER'),
            'PATCH',
            '/sandbox/cobr/tx1/status',
            {'status': 'CANCELADA', 'razao': 'OTHER'},
        ),
    ],
)
def test_metodos_sandbox(
    inter: InterPixAPI, chamada, metodo: str, path: str, body: dict
) -> None:  # type: ignore[no-untyped-def]
    inter.session.request.return_value = make_response(200, {'ok': True})
    assert chamada(inter) == {'ok': True}
    assert_requisicao(inter.session, metodo, f'{SANDBOX_BASE}{path}', json=body)


def test_metodo_sandbox_sem_corpo_devolve_dict_vazio(inter: InterPixAPI) -> None:
    inter.session.request.return_value = make_response(201)
    assert inter.sandbox_pagar_cob('tx1', 1) == {}


def test_metodo_sandbox_recusado_em_producao(inter_prod: InterPixAPI) -> None:
    with pytest.raises(ValueError, match='Sandbox'):
        inter_prod.sandbox_pagar_cob('tx1', 1)
    # Recusa antes de pedir token ou chamar o PSP
    inter_prod.oauth.get_token.assert_not_called()
    inter_prod.session.request.assert_not_called()


def test_metodo_sandbox_recusado_em_sandbox_mode() -> None:
    # sandbox_mode usa token fixo, que o Sandbox do Inter não aceita
    api = InterPixAPI(oauth=_oauth(), sandbox_mode=True)
    api.session.request = Mock()  # type: ignore[method-assign]
    with pytest.raises(ValueError, match='homologacao=True'):
        api.sandbox_pagar_cob('tx1', 1)
    api.session.request.assert_not_called()
