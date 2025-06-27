import os
import pytest
from pypix_api.banks.sicoob import SicoobPixAPI

@pytest.fixture(scope="module")
def sicoob_pix_api():
    """
    Instancia o cliente SicoobPixAPI em modo sandbox usando variáveis de ambiente.
    """
    client_id = os.environ.get("SICOOB_CLIENT_ID")
    cert = os.environ.get("SICOOB_CERT_PATH")
    pvk = os.environ.get("SICOOB_PVK_PATH")
    cert_pfx = os.environ.get("SICOOB_CERT_PFX_PATH")
    pwd_pfx = os.environ.get("SICOOB_PFX_PASSWORD")

    # O usuário pode fornecer cert/pvk OU cert_pfx/pwd_pfx
    api = SicoobPixAPI(
        client_id=client_id,
        cert=cert,
        pvk=pvk,
        cert_pfx=cert_pfx,
        pwd_pfx=pwd_pfx,
        sandbox_mode=True,
    )
    return api

def test_consultar_cobs(sicoob_pix_api):
    """
    Testa a consulta de cobranças no sandbox do Sicoob.
    """
    # Parâmetros mínimos para consulta (ajuste conforme necessário)
    params = {
        "inicio": "2024-01-01T00:00:00Z",
        "fim": "2024-12-31T23:59:59Z",
        "pagina_atual": 0,
        "itens_por_pagina": 1,
    }
    resultado = sicoob_pix_api.consultar_cobs(**params)
    assert "cobs" in resultado
