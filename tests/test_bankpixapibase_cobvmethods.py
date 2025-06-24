from unittest.mock import MagicMock
import pytest

from pypix_api.banks.base import BankPixAPIBase

class DummyBankPixAPIBase(BankPixAPIBase):
    BASE_URL = "https://dummy"
    TOKEN_URL = "https://dummy/token"
    SCOPES = ["dummy.scope"]

    def __init__(self):
        # Não chama o __init__ original para evitar dependências reais
        pass

    def _create_headers(self):
        return {"Authorization": "Bearer dummy", "Content-Type": "application/json", "client_id": "id"}

    def get_base_url(self):
        return self.BASE_URL

@pytest.fixture
def dummy_bank_pix_api():
    api = DummyBankPixAPIBase()
    api.session = MagicMock()
    return api

def test_criar_cobv(dummy_bank_pix_api):
    dummy_bank_pix_api.session.put.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    txid = "txid_cobv"
    body = {"valor": 123}
    result = dummy_bank_pix_api.criar_cobv(txid, body)
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.put.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.put.call_args
    assert txid in args[0]
    assert kwargs["json"] == body

def test_revisar_cobv(dummy_bank_pix_api):
    dummy_bank_pix_api.session.patch.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    txid = "txid_cobv_revisar"
    body = {"valor": 456}
    result = dummy_bank_pix_api.revisar_cobv(txid, body)
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.patch.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.patch.call_args
    assert txid in args[0]
    assert kwargs["json"] == body

def test_consultar_cobv(dummy_bank_pix_api):
    dummy_bank_pix_api.session.get.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    txid = "txid_cobv_consultar"
    result = dummy_bank_pix_api.consultar_cobv(txid, None)
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.get.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.get.call_args
    assert txid in args[0]

def test_listar_cobv(dummy_bank_pix_api):
    dummy_bank_pix_api.session.get.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    # Provide required 'inicio' and 'fim' arguments
    result = dummy_bank_pix_api.listar_cobv("2024-01-01", "2024-12-31")
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.get.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.get.call_args
    assert args[0].endswith("/cobv")
