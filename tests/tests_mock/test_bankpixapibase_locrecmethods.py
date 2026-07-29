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


def test_criar_location_rec(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200,
        {
            'id': 789,
            'location': 'pix.example.com/qr/rec/xyz789',
            'criacao': '2024-01-01T10:00:00Z',
        },
    )
    result = dummy_bank_pix_api.criar_location_rec()
    assert result['id'] == 789
    assert 'location' in result
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert args[1].endswith('/locrec')
    assert kwargs['json'] == {}


def test_listar_locations_rec(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200,
        {
            'parametros': {
                'inicio': '2024-01-01T00:00:00Z',
                'fim': '2024-01-31T23:59:59Z',
            },
            'locrec': [{'id': 1}, {'id': 2}],
        },
    )
    result = dummy_bank_pix_api.listar_locations_rec(
        inicio='2024-01-01T00:00:00Z',
        fim='2024-01-31T23:59:59Z',
    )
    assert 'locrec' in result
    assert len(result['locrec']) == 2
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert args[1].endswith('/locrec')
    assert kwargs['params']['inicio'] == '2024-01-01T00:00:00Z'
    assert kwargs['params']['fim'] == '2024-01-31T23:59:59Z'


def test_listar_locations_rec_com_filtros(
    dummy_bank_pix_api: DummyBankPixAPIBase,
) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(200, {'locrec': []})
    dummy_bank_pix_api.listar_locations_rec(
        inicio='2024-01-01T00:00:00Z',
        fim='2024-01-31T23:59:59Z',
        id_rec_presente=True,
        pagina_atual=0,
        itens_por_pagina=50,
    )
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert kwargs['params']['idRecPresente'] == 'true'
    assert kwargs['params']['paginacao.paginaAtual'] == '0'
    assert kwargs['params']['paginacao.itensPorPagina'] == '50'


def test_consultar_location_rec(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200,
        {
            'id': 789,
            'location': 'pix.example.com/qr/rec/xyz789',
            'criacao': '2024-01-01T10:00:00Z',
            'idRec': 'RR1234567820240115abcdefghijk',
        },
    )
    result = dummy_bank_pix_api.consultar_location_rec(id_loc=789)
    assert result['id'] == 789
    assert result['idRec'] == 'RR1234567820240115abcdefghijk'
    dummy_bank_pix_api.session.request.assert_called_once()
    args, _ = dummy_bank_pix_api.session.request.call_args
    assert '/locrec/789' in args[1]


def test_desvincular_idrec_location(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200,
        {
            'id': 789,
            'location': 'pix.example.com/qr/rec/xyz789',
            'criacao': '2024-01-01T10:00:00Z',
        },
    )
    result = dummy_bank_pix_api.desvincular_idrec_location(id_loc=789)
    assert result['id'] == 789
    assert 'idRec' not in result
    dummy_bank_pix_api.session.request.assert_called_once()
    args, _ = dummy_bank_pix_api.session.request.call_args
    assert '/locrec/789/idRec' in args[1]
