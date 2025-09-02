"""
Testes para os métodos de criação, revisão, consulta e listagem de CobR
"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.base import BankPixAPIBase


class DummyBankPixAPIBase(BankPixAPIBase):
    BASE_URL = 'https://dummy'
    TOKEN_URL = 'https://dummy/token'
    SCOPES = ['dummy.scope']

    def __init__(self, oauth: OAuth2Client) -> None:
        super().__init__(oauth)

    def _create_headers(self) -> dict:
        return {
            'Authorization': 'Bearer dummy',
            'Content-Type': 'application/json',
            'client_id': 'id',
        }

    def get_base_url(self) -> str:
        return self.BASE_URL

    def get_bank_code(self) -> str:
        return 'DUMMY'


@pytest.fixture
def dummy_bank_pix_api() -> DummyBankPixAPIBase:
    mock_oauth = MagicMock()
    mock_oauth.session = MagicMock()
    api = DummyBankPixAPIBase(oauth=mock_oauth)
    return api


def test_criar_cobr_com_txid(dummy_bank_pix_api) -> None:
    dummy_bank_pix_api.session.put.return_value = MagicMock(
        json=lambda: {'result': 'ok'}, raise_for_status=lambda: None
    )
    txid = 'txid_cobr'
    body = {'valor': 123}
    result = dummy_bank_pix_api.criar_cobr_com_txid(txid, body)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.put.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.put.call_args
    assert txid in args[0]
    assert kwargs['json'] == body


def test_revisar_cobr(dummy_bank_pix_api) -> None:
    dummy_bank_pix_api.session.patch.return_value = MagicMock(
        json=lambda: {'result': 'ok'}, raise_for_status=lambda: None
    )
    txid = 'txid_cobr_revisar'
    body = {'valor': 456}
    result = dummy_bank_pix_api.revisar_cobr(txid, body)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.patch.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.patch.call_args
    assert txid in args[0]
    assert kwargs['json'] == body


def test_consultar_cobr(dummy_bank_pix_api) -> None:
    dummy_bank_pix_api.session.get.return_value = MagicMock(
        json=lambda: {'result': 'ok'}, raise_for_status=lambda: None
    )
    txid = 'txid_cobr_consultar'
    result = dummy_bank_pix_api.consultar_cobr(txid)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.get.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.get.call_args
    assert txid in args[0]


def test_criar_cobr(dummy_bank_pix_api) -> None:
    dummy_bank_pix_api.session.post.return_value = MagicMock(
        json=lambda: {'result': 'ok'}, raise_for_status=lambda: None
    )
    body = {'valor': 789}
    result = dummy_bank_pix_api.criar_cobr(body)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.post.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.post.call_args
    assert args[0].endswith('/cobr')
    assert kwargs['json'] == body


def test_consultar_lista_cobr(dummy_bank_pix_api) -> None:
    dummy_bank_pix_api.session.get.return_value = MagicMock(
        json=lambda: {'result': 'ok'}, raise_for_status=lambda: None
    )
    result = dummy_bank_pix_api.consultar_lista_cobr('2024-01-01', '2024-12-31')
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.get.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.get.call_args
    assert args[0].endswith('/cobr')


def test_consultar_lista_cobr_cpf_cnpj_error(dummy_bank_pix_api) -> None:
    """Testa erro quando CPF e CNPJ são fornecidos simultaneamente."""
    with pytest.raises(
        ValueError, match='CPF e CNPJ não podem ser utilizados simultaneamente'
    ):
        dummy_bank_pix_api.consultar_lista_cobr(
            '2024-01-01T00:00:00Z',
            '2024-01-31T23:59:59Z',
            cpf='12345678901',
            cnpj='12345678000195',
        )


def test_solicitar_retentativa_cobr(dummy_bank_pix_api) -> None:
    dummy_bank_pix_api.session.post.return_value = MagicMock(
        json=lambda: {'result': 'ok'}, raise_for_status=lambda: None
    )
    txid = 'txid_cobr_retentativa'
    data_retentativa = date(2024, 12, 31)
    result = dummy_bank_pix_api.solicitar_retentativa_cobr(txid, data_retentativa)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.post.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.post.call_args
    assert txid in args[0]
    assert '2024-12-31' in args[0]
