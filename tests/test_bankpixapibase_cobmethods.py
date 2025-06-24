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

def test_criar_cob(dummy_bank_pix_api):
    dummy_bank_pix_api.session.put.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    txid = "txid123"
    body = {"valor": 100}
    result = dummy_bank_pix_api.criar_cob(txid, body)
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.put.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.put.call_args
    assert txid in args[0]
    assert kwargs["json"] == body

def test_criar_cob_auto_txid(dummy_bank_pix_api):
    dummy_bank_pix_api.session.post.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    body = {"valor": 200}
    result = dummy_bank_pix_api.criar_cob_auto_txid(body)
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.post.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.post.call_args
    assert args[0].endswith("/cob")
    assert kwargs["json"] == body

def test_revisar_cob(dummy_bank_pix_api):
    dummy_bank_pix_api.session.patch.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    txid = "txid456"
    body = {"valor": 300}
    result = dummy_bank_pix_api.revisar_cob(txid, body)
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.patch.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.patch.call_args
    assert txid in args[0]
    assert kwargs["json"] == body

def test_consultar_cob(dummy_bank_pix_api):
    dummy_bank_pix_api.session.get.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    txid = "txid789"
    result = dummy_bank_pix_api.consultar_cob(txid)
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.get.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.get.call_args
    assert txid in args[0]

def test_consultar_cobs(dummy_bank_pix_api):
    dummy_bank_pix_api.session.get.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    inicio = "2024-01-01T00:00:00Z"
    fim = "2024-01-31T23:59:59Z"
    result = dummy_bank_pix_api.consultar_cobs(inicio, fim, cpf="12345678901")
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.get.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.get.call_args
    assert args[0].endswith("/cob")
    assert kwargs["params"]["inicio"] == inicio
    assert kwargs["params"]["fim"] == fim
    assert kwargs["params"]["cpf"] == "12345678901"

def test_consultar_cobs_cpf_cnpj_error(dummy_bank_pix_api):
    with pytest.raises(ValueError):
        dummy_bank_pix_api.consultar_cobs(
            "2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z", cpf="123", cnpj="456"
        )
