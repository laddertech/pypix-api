"""
Test cases for the Rec methods of BankPixAPIBase.
"""

from unittest.mock import MagicMock

import pytest

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.base import BankPixAPIBase
from tests.conftest import make_response


class DummyBankPixAPIBase(BankPixAPIBase):
    """Dummy implementation of BankPixAPIBase for testing Rec methods."""

    BASE_URL = 'https://dummy'
    TOKEN_URL = 'https://dummy/token'
    SCOPES = ['dummy.scope']

    def __init__(self, oauth: OAuth2Client) -> None:
        super().__init__(oauth)
        # Mantém o mock da sessão nos testes

    def _create_headers(self) -> dict:
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


def test_criar_recorrencia(dummy_bank_pix_api) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    body = {'idRec': 'rec123', 'valor': 500}
    result = dummy_bank_pix_api.criar_recorrencia(body)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert args[1].endswith('/rec')
    assert kwargs['json'] == body


def test_revisar_recorrencia(dummy_bank_pix_api) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    id_rec = 'rec456'
    body = {'valor': 600}
    result = dummy_bank_pix_api.revisar_recorrencia(id_rec, body)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert id_rec in args[1]
    assert kwargs['json'] == body


def test_cancelar_recorrencia(dummy_bank_pix_api) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    id_rec = 'rec_cancelar'
    result = dummy_bank_pix_api.cancelar_recorrencia(id_rec)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert id_rec in args[1]
    assert kwargs['json'] == {'status': 'CANCELADA'}


def test_consultar_recorrencia(dummy_bank_pix_api):
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    id_rec = 'rec789'
    result = dummy_bank_pix_api.consultar_recorrencia(id_rec)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert id_rec in args[1]
    assert 'params' in kwargs
    assert kwargs['params'] == {}


def test_consultar_recorrencia_com_txid(dummy_bank_pix_api):
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    id_rec = 'rec101'
    txid = 'txid999'
    result = dummy_bank_pix_api.consultar_recorrencia(id_rec, txid=txid)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert id_rec in args[1]
    assert kwargs['params']['txid'] == txid


def test_listar_recorrencias(dummy_bank_pix_api):
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    inicio = '2024-01-01T00:00:00Z'
    fim = '2024-01-31T23:59:59Z'
    result = dummy_bank_pix_api.listar_recorrencias(
        inicio,
        fim,
        cpf='12345678901',
        status='ATIVA',
        pagina_atual=1,
        itens_por_pagina=10,
    )
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert args[1].endswith('/rec')
    params = kwargs['params']
    assert params['inicio'] == inicio
    assert params['fim'] == fim
    assert params['cpf'] == '12345678901'
    assert params['status'] == 'ATIVA'
    assert params['paginacao.paginaAtual'] == '1'
    assert params['paginacao.itensPorPagina'] == '10'


def test_listar_recorrencias_cpf_cnpj_error(dummy_bank_pix_api) -> None:
    with pytest.raises(ValueError):
        dummy_bank_pix_api.listar_recorrencias(
            '2024-01-01T00:00:00Z', '2024-01-31T23:59:59Z', cpf='123', cnpj='456'
        )
