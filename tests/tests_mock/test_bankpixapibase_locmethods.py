from typing import ClassVar
from unittest.mock import MagicMock

import pytest

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.base import BankPixAPIBase
from tests.conftest import make_response


class DummyBankPixAPIBase(BankPixAPIBase):
    BASE_URL = 'https://dummy'
    TOKEN_URL = 'https://dummy/token'
    SCOPES: ClassVar[list[str]] = ['dummy.scope']

    def __init__(self, oauth: OAuth2Client) -> None:
        super().__init__(oauth)

    def _create_headers(self) -> dict[str, str]:
        return {
            'Authorization': 'Bearer dummy',
            'Content-Type': 'application/json',
            'client_id': 'id',
        }

    def get_base_url(self) -> str:
        return self.BASE_URL


@pytest.fixture
def dummy_bank_pix_api() -> DummyBankPixAPIBase:
    mock_oauth = MagicMock()
    mock_oauth.session = MagicMock()
    api = DummyBankPixAPIBase(oauth=mock_oauth)
    return api


def test_criar_location(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200,
        {
            'id': 123,
            'location': 'pix.example.com/qr/v2/abc123',
            'tipoCob': 'cob',
            'criacao': '2024-01-01T10:00:00Z',
        },
    )
    result = dummy_bank_pix_api.criar_location(tipo_cob='cob')
    assert result['id'] == 123
    assert result['tipoCob'] == 'cob'
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert args[1].endswith('/loc')
    assert kwargs['json'] == {'tipoCob': 'cob'}


def test_criar_location_cobv(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200,
        {
            'id': 456,
            'location': 'pix.example.com/qr/v2/def456',
            'tipoCob': 'cobv',
            'criacao': '2024-01-01T10:00:00Z',
        },
    )
    result = dummy_bank_pix_api.criar_location(tipo_cob='cobv')
    assert result['id'] == 456
    assert result['tipoCob'] == 'cobv'


def test_listar_locations(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200,
        {
            'parametros': {
                'inicio': '2024-01-01T00:00:00Z',
                'fim': '2024-01-31T23:59:59Z',
            },
            'loc': [{'id': 1}, {'id': 2}],
        },
    )
    result = dummy_bank_pix_api.listar_locations(
        inicio='2024-01-01T00:00:00Z',
        fim='2024-01-31T23:59:59Z',
    )
    assert 'loc' in result
    assert len(result['loc']) == 2
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert args[1].endswith('/loc')
    assert kwargs['params']['inicio'] == '2024-01-01T00:00:00Z'
    assert kwargs['params']['fim'] == '2024-01-31T23:59:59Z'


def test_listar_locations_com_filtros(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(200, {'loc': []})
    dummy_bank_pix_api.listar_locations(
        inicio='2024-01-01T00:00:00Z',
        fim='2024-01-31T23:59:59Z',
        txid_presente=True,
        tipo_cob='cob',
        pagina_atual=0,
        itens_por_pagina=50,
    )
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert kwargs['params']['txIdPresente'] == 'true'
    assert kwargs['params']['tipoCob'] == 'cob'
    assert kwargs['params']['paginacao.paginaAtual'] == '0'
    assert kwargs['params']['paginacao.itensPorPagina'] == '50'


def test_consultar_location(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200,
        {
            'id': 123,
            'location': 'pix.example.com/qr/v2/abc123',
            'tipoCob': 'cob',
            'criacao': '2024-01-01T10:00:00Z',
            'txid': 'txid123',
        },
    )
    result = dummy_bank_pix_api.consultar_location(id_loc=123)
    assert result['id'] == 123
    assert result['txid'] == 'txid123'
    dummy_bank_pix_api.session.request.assert_called_once()
    args, _ = dummy_bank_pix_api.session.request.call_args
    assert '/loc/123' in args[1]


def test_desvincular_txid_location(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200,
        {
            'id': 123,
            'location': 'pix.example.com/qr/v2/abc123',
            'tipoCob': 'cob',
            'criacao': '2024-01-01T10:00:00Z',
        },
    )
    result = dummy_bank_pix_api.desvincular_txid_location(id_loc=123)
    assert result['id'] == 123
    assert 'txid' not in result
    dummy_bank_pix_api.session.request.assert_called_once()
    args, _ = dummy_bank_pix_api.session.request.call_args
    assert '/loc/123/txid' in args[1]
