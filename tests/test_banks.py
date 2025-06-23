import pytest
from unittest.mock import patch, MagicMock
from pypix_api.banks.base import BankPixAPIBase
from pypix_api.banks.bb import BBPixAPI
from pypix_api.banks.sicoob import SicoobPixAPI
from pypix_api.banks.cobv_methods import CobVMethods

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

    import sys
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
