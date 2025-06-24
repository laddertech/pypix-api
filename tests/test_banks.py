from unittest.mock import MagicMock, patch

import pytest

from pypix_api.banks.base import BankPixAPIBase
from pypix_api.banks.bb import BBPixAPI
from pypix_api.banks.cobv_methods import CobVMethods
from pypix_api.banks.sicoob import SicoobPixAPI


class DummyCobVMethods(CobVMethods):
    def criar_cobv(self, txid, body):
        return {"txid": txid, "body": body}
    def revisar_cobv(self, txid, body):
        return {"txid": txid, "body": body}
    def consultar_cobv(self, txid):
        return {"txid": txid}
    def listar_cobv(self):
        return []

def test_bankpixapibase_init():
    class DummyBank(BankPixAPIBase, DummyCobVMethods):
        BASE_URL = "https://dummy"
        TOKEN_URL = "https://dummy/token"
        SCOPES = ["dummy.scope"]

    with patch("pypix_api.banks.base.OAuth2Client", MagicMock()), \
         patch("pypix_api.auth.mtls.get_session_with_mtls", MagicMock(return_value=object())):
        bank = DummyBank("id", "secret", "cert", "key")
        assert hasattr(bank, "session")
        assert hasattr(bank, "oauth")

def test_bb_pix_api_inheritance():
    with patch("pypix_api.banks.base.OAuth2Client", MagicMock()), \
         patch("pypix_api.auth.mtls.get_session_with_mtls", MagicMock(return_value=object())):
        api = BBPixAPI("id", "secret", "cert", "key")
        assert isinstance(api, BankPixAPIBase)

def test_sicoob_pix_api_inheritance():
    with patch("pypix_api.banks.base.OAuth2Client", MagicMock()), \
         patch("pypix_api.auth.mtls.get_session_with_mtls", MagicMock(return_value=object())):
        api = SicoobPixAPI("id", "secret", "cert", "key")
        assert isinstance(api, BankPixAPIBase)

def test_cobv_methods_criar():
    cobv = DummyCobVMethods()
    result = cobv.criar_cobv("123", {"valor": 10})
    assert result["txid"] == "123"
    assert result["body"]["valor"] == 10

# Testes para métodos herdados de CobMethods em BankPixAPIBase

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

# Testes para métodos de RecMethods

def test_criar_recorrencia(dummy_bank_pix_api):
    dummy_bank_pix_api.session.put.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    id_rec = "rec123"
    body = {"valor": 500}
    result = dummy_bank_pix_api.criar_recorrencia(id_rec, body)
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.put.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.put.call_args
    assert id_rec in args[0]
    assert kwargs["json"] == body

def test_revisar_recorrencia(dummy_bank_pix_api):
    dummy_bank_pix_api.session.patch.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    id_rec = "rec456"
    body = {"valor": 600}
    result = dummy_bank_pix_api.revisar_recorrencia(id_rec, body)
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.patch.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.patch.call_args
    assert id_rec in args[0]
    assert kwargs["json"] == body

def test_consultar_recorrencia(dummy_bank_pix_api):
    dummy_bank_pix_api.session.get.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    id_rec = "rec789"
    result = dummy_bank_pix_api.consultar_recorrencia(id_rec)
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.get.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.get.call_args
    assert id_rec in args[0]
    assert "params" in kwargs
    assert kwargs["params"] == {}

def test_consultar_recorrencia_com_txid(dummy_bank_pix_api):
    dummy_bank_pix_api.session.get.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    id_rec = "rec101"
    txid = "txid999"
    result = dummy_bank_pix_api.consultar_recorrencia(id_rec, txid=txid)
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.get.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.get.call_args
    assert id_rec in args[0]
    assert kwargs["params"]["txid"] == txid

def test_listar_recorrencias(dummy_bank_pix_api):
    dummy_bank_pix_api.session.get.return_value = MagicMock(
        json=lambda: {"result": "ok"}, raise_for_status=lambda: None
    )
    inicio = "2024-01-01T00:00:00Z"
    fim = "2024-01-31T23:59:59Z"
    result = dummy_bank_pix_api.listar_recorrencias(inicio, fim, cpf="12345678901", status="ATIVA", pagina_atual=1, itens_por_pagina=10)
    assert result == {"result": "ok"}
    dummy_bank_pix_api.session.get.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.get.call_args
    assert args[0].endswith("/rec")
    params = kwargs["params"]
    assert params["inicio"] == inicio
    assert params["fim"] == fim
    assert params["cpf"] == "12345678901"
    assert params["status"] == "ATIVA"
    assert params["paginaAtual"] == 1
    assert params["itensPorPagina"] == 10

def test_listar_recorrencias_cpf_cnpj_error(dummy_bank_pix_api):
    with pytest.raises(ValueError):
        dummy_bank_pix_api.listar_recorrencias(
            "2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z", cpf="123", cnpj="456"
        )
