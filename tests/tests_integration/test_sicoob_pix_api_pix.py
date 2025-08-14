"""
Teste de integração com a API do Sicoob para operações PIX em modo Sandbox
"""

import os
from datetime import datetime, timedelta

import pytest

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.sicoob import SicoobPixAPI


@pytest.fixture(scope="module")
def sicoob_pix_api():
    """
    Instancia o cliente SicoobPixAPI em modo sandbox usando variáveis de ambiente.
    """
    client_id = os.environ.get("CLIENT_ID")
    cert = os.environ.get("CERT")
    pvk = os.environ.get("PVK")
    cert_pfx = os.environ.get("CERT_PFX")
    pwd_pfx = os.environ.get("PWD_PFX")

    # Primeiro, cria o cliente OAuth2
    oauth_client = OAuth2Client(
        token_url=SicoobPixAPI.TOKEN_URL,
        client_id=client_id,
        cert=cert,
        pvk=pvk,
        cert_pfx=cert_pfx,
        pwd_pfx=pwd_pfx,
        sandbox_mode=True,
    )

    # Depois, cria a API com o cliente OAuth2
    api = SicoobPixAPI(
        oauth=oauth_client,
        sandbox_mode=True,
    )
    return api


def test_consultar_pix(sicoob_pix_api):
    """
    Testa a consulta de PIX recebidos no sandbox do Sicoob.
    """
    # Define período de consulta (últimos 30 dias)
    fim = datetime.now()
    inicio = fim - timedelta(days=30)

    params = {
        "inicio": inicio.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fim": fim.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pagina_atual": 0,
        "itens_por_pagina": 10,
    }
    resultado = sicoob_pix_api.consultar_pix(**params)

    # Verifica se a resposta tem a estrutura esperada
    assert isinstance(resultado, dict)
    # A resposta pode ter "pix" ou estar vazia se não houver transações


def test_consultar_pix_com_filtros(sicoob_pix_api):
    """
    Testa a consulta de PIX com filtros adicionais.
    """
    fim = datetime.now()
    inicio = fim - timedelta(days=7)

    params = {
        "inicio": inicio.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fim": fim.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "txid_presente": True,
        "devolucao_presente": False,
        "pagina_atual": 0,
        "itens_por_pagina": 5,
    }
    resultado = sicoob_pix_api.consultar_pix(**params)

    assert isinstance(resultado, dict)


def test_consultar_pix_com_cpf(sicoob_pix_api):
    """
    Testa a consulta de PIX filtrado por CPF.
    """
    fim = datetime.now()
    inicio = fim - timedelta(days=30)

    params = {
        "inicio": inicio.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fim": fim.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cpf": "12345678909",
        "pagina_atual": 0,
        "itens_por_pagina": 10,
    }
    resultado = sicoob_pix_api.consultar_pix(**params)

    assert isinstance(resultado, dict)


def test_consultar_pix_validacao_cpf_cnpj(sicoob_pix_api):
    """
    Testa a validação que impede usar CPF e CNPJ simultaneamente.
    """
    fim = datetime.now()
    inicio = fim - timedelta(days=7)

    with pytest.raises(ValueError, match="CPF e CNPJ não podem ser utilizados simultaneamente"):
        sicoob_pix_api.consultar_pix(
            inicio=inicio.strftime("%Y-%m-%dT%H:%M:%SZ"),
            fim=fim.strftime("%Y-%m-%dT%H:%M:%SZ"),
            cpf="12345678909",
            cnpj="12345678000195"
        )


@pytest.mark.skip(reason="Requer e2eid válido de transação existente")
def test_consultar_pix_por_e2eid(sicoob_pix_api):
    """
    Testa a consulta de PIX individual por e2eid.
    Este teste é pulado por padrão pois requer um e2eid válido.
    """
    # Substitua por um e2eid válido do sandbox
    e2eid = "E12345678202301011200abcdef123456"

    resultado = sicoob_pix_api.consultar_pix_por_e2eid(e2eid)

    assert isinstance(resultado, dict)
    assert "endToEndId" in resultado


@pytest.mark.skip(reason="Requer e2eid válido e pode afetar dados do sandbox")
def test_solicitar_devolucao_pix(sicoob_pix_api):
    """
    Testa a solicitação de devolução de PIX.
    Este teste é pulado por padrão pois requer um e2eid válido e pode afetar dados.
    """
    # Substitua por um e2eid válido do sandbox
    e2eid = "E12345678202301011200abcdef123456"
    id_devolucao = f"devolucao_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    body = {
        "valor": "1.00",
        "natureza": "ORIGINAL",
        "descricao": "Teste de devolução via integração"
    }

    resultado = sicoob_pix_api.solicitar_devolucao_pix(e2eid, id_devolucao, body)

    assert isinstance(resultado, dict)
    assert "id" in resultado
    assert "valor" in resultado


@pytest.mark.skip(reason="Requer e2eid e id_devolucao válidos")
def test_consultar_devolucao_pix(sicoob_pix_api):
    """
    Testa a consulta de devolução de PIX.
    Este teste é pulado por padrão pois requer e2eid e id_devolucao válidos.
    """
    # Substitua por valores válidos do sandbox
    e2eid = "E12345678202301011200abcdef123456"
    id_devolucao = "devolucao_20240101120000"

    resultado = sicoob_pix_api.consultar_devolucao_pix(e2eid, id_devolucao)

    assert isinstance(resultado, dict)
    assert "id" in resultado
    assert "status" in resultado
