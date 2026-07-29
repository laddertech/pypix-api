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
        # Mantém o mock da sessão nos testes

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


def test_criar_cob(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    txid = 'txid123'
    body = {'valor': 100}
    result = dummy_bank_pix_api.criar_cob(txid, body)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert txid in args[1]
    assert kwargs['json'] == body


def test_criar_cob_auto_txid(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    body = {'valor': 200}
    result = dummy_bank_pix_api.criar_cob_auto_txid(body)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert args[1].endswith('/cob')
    assert kwargs['json'] == body


def test_revisar_cob(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    txid = 'txid456'
    body = {'valor': 300}
    result = dummy_bank_pix_api.revisar_cob(txid, body)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert txid in args[1]
    assert kwargs['json'] == body


def test_consultar_cob(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    txid = 'txid789'
    result = dummy_bank_pix_api.consultar_cob(txid)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert txid in args[1]


def test_consultar_cobs(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    inicio = '2024-01-01T00:00:00Z'
    fim = '2024-01-31T23:59:59Z'
    result = dummy_bank_pix_api.consultar_cobs(inicio, fim, cpf='12345678901')
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert args[1].endswith('/cob')
    assert kwargs['params']['inicio'] == inicio
    assert kwargs['params']['fim'] == fim
    assert kwargs['params']['cpf'] == '12345678901'


def test_consultar_cobs_cpf_cnpj_error(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    with pytest.raises(ValueError):
        dummy_bank_pix_api.consultar_cobs(
            '2024-01-01T00:00:00Z', '2024-01-31T23:59:59Z', cpf='123', cnpj='456'
        )
