from unittest.mock import MagicMock

import pytest

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.base import BankPixAPIBase
from tests.conftest import make_response


class DummyBankPixAPIBaseSolicRec(BankPixAPIBase):
    """Dummy implementation of BankPixAPIBase for testing SolicRec methods."""

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
def dummy_bank_pix_api() -> DummyBankPixAPIBaseSolicRec:
    mock_oauth = MagicMock()
    mock_oauth.session = MagicMock()
    api = DummyBankPixAPIBaseSolicRec(oauth=mock_oauth)
    return api


def test_criar_solicrec(dummy_bank_pix_api) -> None:
    """Test criar_solicrec method."""
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    body = {
        'calendario': {'expiracao': 3600},
        'devedor': {'cpf': '12345678909', 'nome': 'Fulano'},
    }
    result = dummy_bank_pix_api.criar_solicrec(body)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert args[1].endswith('/solicrec')
    assert kwargs['json'] == body
    assert 'headers' in kwargs


def test_consultar_solicrec(dummy_bank_pix_api) -> None:
    """Test consultar_solicrec method."""
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    id_solic_rec = 'solic123'
    result = dummy_bank_pix_api.consultar_solicrec(id_solic_rec)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert id_solic_rec in args[1]
    assert 'headers' in kwargs


def test_revisar_solicrec(dummy_bank_pix_api) -> None:
    """Test revisar_solicrec method."""
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    id_solic_rec = 'solic456'
    body = {'status': 'CANCELADA'}
    result = dummy_bank_pix_api.revisar_solicrec(id_solic_rec, body)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert id_solic_rec in args[1]
    assert kwargs['json'] == body
    assert 'headers' in kwargs


def test_cancelar_solicrec(dummy_bank_pix_api) -> None:
    """Test cancelar_solicrec method."""
    dummy_bank_pix_api.session.request.return_value = make_response(
        200, {'result': 'ok'}
    )
    id_solic_rec = 'solic789'
    result = dummy_bank_pix_api.cancelar_solicrec(id_solic_rec)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert id_solic_rec in args[1]
    assert kwargs['json'] == {'status': 'CANCELADA'}
    assert 'headers' in kwargs
