from unittest.mock import MagicMock

import pytest

from pypix_api.banks.bb import BBPixAPI
from tests.conftest import make_response


@pytest.fixture
def bb_pix_api() -> BBPixAPI:
    mock_oauth = MagicMock()
    mock_oauth.session = MagicMock()
    mock_oauth.client_id = 'test-client-id'
    api = BBPixAPI(oauth=mock_oauth, sandbox_mode=True)
    return api


def test_consultar_pix_bb_basico(bb_pix_api: BBPixAPI) -> None:
    bb_pix_api.session.request.return_value = make_response(
        200,
        {
            'parametros': {
                'inicio': '2024-01-01T00:00:00Z',
                'fim': '2024-01-31T23:59:59Z',
            },
            'pix': [{'endToEndId': 'E12345678202401011200abc', 'valor': '100.00'}],
        },
    )
    result = bb_pix_api.consultar_pix_bb(
        inicio='2024-01-01T00:00:00Z',
        fim='2024-01-31T23:59:59Z',
    )
    assert 'pix' in result
    bb_pix_api.session.request.assert_called_once()
    args, kwargs = bb_pix_api.session.request.call_args
    assert '/pix-bb' in args[1]
    assert kwargs['params']['inicio'] == '2024-01-01T00:00:00Z'
    assert kwargs['params']['fim'] == '2024-01-31T23:59:59Z'


def test_consultar_pix_bb_com_chave(bb_pix_api: BBPixAPI) -> None:
    bb_pix_api.session.request.return_value = make_response(200, {'pix': []})
    bb_pix_api.consultar_pix_bb(
        inicio='2024-01-01T00:00:00Z',
        fim='2024-01-31T23:59:59Z',
        chave='email@exemplo.com',
    )
    args, kwargs = bb_pix_api.session.request.call_args
    assert kwargs['params']['chave'] == 'email@exemplo.com'


def test_consultar_pix_bb_com_contestacao(bb_pix_api: BBPixAPI) -> None:
    bb_pix_api.session.request.return_value = make_response(200, {'pix': []})
    bb_pix_api.consultar_pix_bb(
        inicio='2024-01-01T00:00:00Z',
        fim='2024-01-31T23:59:59Z',
        contestacao_presente=True,
    )
    args, kwargs = bb_pix_api.session.request.call_args
    assert kwargs['params']['contestacaoPresente'] == 'true'


def test_consultar_pix_bb_todos_filtros(bb_pix_api: BBPixAPI) -> None:
    bb_pix_api.session.request.return_value = make_response(200, {'pix': []})
    bb_pix_api.consultar_pix_bb(
        inicio='2024-01-01T00:00:00Z',
        fim='2024-01-31T23:59:59Z',
        txid='txid123',
        txid_presente=True,
        devolucao_presente=False,
        contestacao_presente=True,
        cpf='12345678901',
        chave='email@exemplo.com',
        pagina_atual=0,
        itens_por_pagina=50,
    )
    args, kwargs = bb_pix_api.session.request.call_args
    assert kwargs['params']['txid'] == 'txid123'
    assert kwargs['params']['txIdPresente'] == 'true'
    assert kwargs['params']['devolucaoPresente'] == 'false'
    assert kwargs['params']['contestacaoPresente'] == 'true'
    assert kwargs['params']['cpf'] == '12345678901'
    assert kwargs['params']['chave'] == 'email@exemplo.com'
    assert kwargs['params']['paginacao.paginaAtual'] == '0'
    assert kwargs['params']['paginacao.itensPorPagina'] == '50'


def test_consultar_pix_bb_cpf_cnpj_error(bb_pix_api: BBPixAPI) -> None:
    with pytest.raises(
        ValueError, match='CPF e CNPJ não podem ser utilizados simultaneamente'
    ):
        bb_pix_api.consultar_pix_bb(
            inicio='2024-01-01T00:00:00Z',
            fim='2024-01-31T23:59:59Z',
            cpf='12345678901',
            cnpj='12345678901234',
        )


def test_consultar_devolucoes_bb_basico(bb_pix_api: BBPixAPI) -> None:
    bb_pix_api.session.request.return_value = make_response(
        200,
        {
            'parametros': {
                'inicio': '2024-01-01T00:00:00Z',
                'fim': '2024-01-31T23:59:59Z',
            },
            'devolucoes': [{'id': 'dev123', 'valor': '50.00', 'status': 'DEVOLVIDO'}],
        },
    )
    result = bb_pix_api.consultar_devolucoes_bb(
        inicio='2024-01-01T00:00:00Z',
        fim='2024-01-31T23:59:59Z',
    )
    assert 'devolucoes' in result
    bb_pix_api.session.request.assert_called_once()
    args, kwargs = bb_pix_api.session.request.call_args
    assert '/pix-bb/devolucoes' in args[1]


def test_consultar_devolucoes_bb_com_estado(bb_pix_api: BBPixAPI) -> None:
    bb_pix_api.session.request.return_value = make_response(200, {'devolucoes': []})
    bb_pix_api.consultar_devolucoes_bb(
        inicio='2024-01-01T00:00:00Z',
        fim='2024-01-31T23:59:59Z',
        estado_devolucao='DEVOLVIDO',
    )
    args, kwargs = bb_pix_api.session.request.call_args
    assert kwargs['params']['estadoDevolucao'] == 'DEVOLVIDO'


def test_consultar_devolucoes_bb_todos_estados(bb_pix_api: BBPixAPI) -> None:
    """Testa todos os estados possíveis de devolução."""
    estados = ['EM_PROCESSAMENTO', 'DEVOLVIDO', 'NAO_REALIZADO', 'DEVOLUCAO_MED']
    for estado in estados:
        bb_pix_api.session.request.return_value = make_response(200, {'devolucoes': []})
        bb_pix_api.consultar_devolucoes_bb(
            inicio='2024-01-01T00:00:00Z',
            fim='2024-01-31T23:59:59Z',
            estado_devolucao=estado,
        )
        args, kwargs = bb_pix_api.session.request.call_args
        assert kwargs['params']['estadoDevolucao'] == estado


def test_consultar_devolucoes_bb_cpf_cnpj_error(bb_pix_api: BBPixAPI) -> None:
    with pytest.raises(
        ValueError, match='CPF e CNPJ não podem ser utilizados simultaneamente'
    ):
        bb_pix_api.consultar_devolucoes_bb(
            inicio='2024-01-01T00:00:00Z',
            fim='2024-01-31T23:59:59Z',
            cpf='12345678901',
            cnpj='12345678901234',
        )


def test_bb_urls_v2(bb_pix_api: BBPixAPI) -> None:
    """Testa se as URLs do BB estão na versão v2."""
    assert 'v2' in bb_pix_api.BASE_URL
    assert 'v2' in bb_pix_api.SANDBOX_BASE_URL
    assert 'api-pix.bb.com.br' in bb_pix_api.BASE_URL
    assert 'api-pix.hm.bb.com.br' in bb_pix_api.SANDBOX_BASE_URL
