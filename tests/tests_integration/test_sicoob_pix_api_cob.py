"""
Teste de integração com a API do Sicoob em modo Sandbox
"""

import os

import pytest

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.sicoob import SicoobPixAPI


@pytest.fixture(scope='module')
def sicoob_pix_api():
    """
    Instancia o cliente SicoobPixAPI em modo sandbox usando variáveis de ambiente.
    """
    client_id = os.environ.get('CLIENT_ID')
    cert = os.environ.get('CERT')
    pvk = os.environ.get('PVK')
    cert_pfx = os.environ.get('CERT_PFX')
    pwd_pfx = os.environ.get('PWD_PFX')

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


@pytest.fixture(scope='module')
def cob_criada(sicoob_pix_api):
    """
    Cria uma cobrança via criar_cob_auto_txid e retorna o resultado.
    """
    body = {
        'calendario': {'expiracao': 3600},
        'devedor': {'cpf': '12345678909', 'nome': 'Cliente Teste'},
        'valor': {'original': '1.00'},
        'chave': 'testechavepix@teste.com.br',
        'solicitacaoPagador': 'Teste integração Sicoob',
    }
    resultado = sicoob_pix_api.criar_cob_auto_txid(body)
    return resultado


def test_consultar_cobs(sicoob_pix_api):
    """
    Testa a consulta de cobranças no sandbox do Sicoob.
    """
    params = {
        'inicio': '2024-01-01T00:00:00Z',
        'fim': '2024-12-31T23:59:59Z',
        'pagina_atual': 0,
        'itens_por_pagina': 1,
    }
    resultado = sicoob_pix_api.consultar_cobs(**params)
    assert 'cobs' in resultado


def test_criar_cob_auto_txid(cob_criada):
    """
    Testa a criação de cobrança automática (txid gerado pela API).
    """
    assert 'txid' in cob_criada
    assert 'loc' in cob_criada


def test_revisar_cob(sicoob_pix_api, cob_criada):
    """
    Testa a revisão de uma cobrança criada.
    """
    txid = cob_criada['txid']
    body = {'valor': {'original': '2.00'}, 'solicitacaoPagador': 'Cobrança revisada'}
    resultado = sicoob_pix_api.revisar_cob(txid, body)
    assert 'valor' in resultado
    assert 'solicitacaoPagador' in resultado


def test_consultar_cob(sicoob_pix_api, cob_criada):
    """
    Testa a consulta de uma cobrança criada.
    """
    txid = cob_criada['txid']
    resultado = sicoob_pix_api.consultar_cob(txid)
    assert 'valor' in resultado
    assert 'txid' in resultado
    assert 'location' in resultado
