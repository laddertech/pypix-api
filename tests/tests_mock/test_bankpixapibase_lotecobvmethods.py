from typing import ClassVar
from unittest.mock import MagicMock

import pytest

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.base import BankPixAPIBase
from pypix_api.banks.exceptions import (
    PixAcessoNegadoException,
    PixErroServicoIndisponivelException,
    PixErroValidacaoException,
    PixRecursoNaoEncontradoException,
)
from tests.conftest import make_response


class DummyBankPixAPIBase(BankPixAPIBase):
    BASE_URL = 'https://dummy'
    TOKEN_URL = 'https://dummy/token'
    SCOPES: ClassVar[list[str]] = ['dummy.scope']

    def __init__(self, oauth: OAuth2Client) -> None:
        super().__init__(oauth)

    def _create_headers(self) -> dict[str, str]:
        return {
            'Authorization': 'Bearer dummy',
            'Content-Type': 'application/json',
            'client_id': 'id',
        }

    def get_base_url(self) -> str:
        return self.BASE_URL

    def get_bank_code(self) -> str:
        return 'dummy'


@pytest.fixture
def dummy_bank_pix_api() -> DummyBankPixAPIBase:
    mock_oauth = MagicMock()
    mock_oauth.session = MagicMock()
    api = DummyBankPixAPIBase(oauth=mock_oauth)
    return api


def test_criar_lote_cobv(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    """Testa a criação de um lote de cobranças com vencimento."""
    expected_response = {
        'id': 'lote123',
        'descricao': 'Lote de teste',
        'status': 'EM_PROCESSAMENTO',
        'criacao': '2024-01-01T00:00:00Z',
    }

    dummy_bank_pix_api.session.request.return_value = make_response(
        200, expected_response
    )

    id_lote = 'lote123'
    body = {
        'descricao': 'Lote de teste',
        'cobsv': [
            {
                'txid': 'txid123',
                'calendario': {'dataDeVencimento': '2024-12-31'},
                'devedor': {'cpf': '12345678901', 'nome': 'João'},
                'valor': {'original': '100.00'},
                'chave': 'chave@exemplo.com',
            }
        ],
    }

    result = dummy_bank_pix_api.criar_lote_cobv(id_lote, body)

    assert result == expected_response
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert id_lote in args[1]
    assert args[1].endswith(f'/lotecobv/{id_lote}')
    assert kwargs['json'] == body


def test_alterar_lote_cobv(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    """Testa a alteração de um lote de cobranças com vencimento."""
    expected_response = {
        'id': 'lote456',
        'descricao': 'Lote alterado',
        'status': 'EM_PROCESSAMENTO',
        'revisao': 1,
    }

    dummy_bank_pix_api.session.request.return_value = make_response(
        200, expected_response
    )

    id_lote = 'lote456'
    body = {
        'descricao': 'Lote alterado',
        'cobsv': [
            {
                'txid': 'txid456',
                'calendario': {'dataDeVencimento': '2024-12-31'},
                'devedor': {'cpf': '98765432100', 'nome': 'Maria'},
                'valor': {'original': '200.00'},
                'chave': 'chave2@exemplo.com',
            }
        ],
    }

    result = dummy_bank_pix_api.alterar_lote_cobv(id_lote, body)

    assert result == expected_response
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert id_lote in args[1]
    assert args[1].endswith(f'/lotecobv/{id_lote}')
    assert kwargs['json'] == body


def test_consultar_lote_cobv(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    """Testa a consulta de um lote de cobranças com vencimento por ID."""
    expected_response = {
        'id': 'lote789',
        'descricao': 'Lote consultado',
        'status': 'CRIADO',
        'criacao': '2024-01-01T00:00:00Z',
        'cobsv': [
            {
                'txid': 'txid789',
                'status': 'ATIVA',
                'calendario': {'dataDeVencimento': '2024-12-31'},
                'devedor': {'cpf': '11111111111', 'nome': 'Pedro'},
                'valor': {'original': '300.00'},
                'chave': 'chave3@exemplo.com',
            }
        ],
    }

    dummy_bank_pix_api.session.request.return_value = make_response(
        200, expected_response
    )

    id_lote = 'lote789'
    result = dummy_bank_pix_api.consultar_lote_cobv(id_lote)

    assert result == expected_response
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert id_lote in args[1]
    assert args[1].endswith(f'/lotecobv/{id_lote}')
    assert 'params' not in kwargs or kwargs['params'] == {}


def test_listar_lotes_cobv(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    """Testa a listagem de lotes de cobranças com vencimento."""
    expected_response = {
        'parametros': {
            'inicio': '2024-01-01T00:00:00Z',
            'fim': '2024-01-31T23:59:59Z',
            'paginacao': {'paginaAtual': 0, 'itensPorPagina': 10},
        },
        'lotes': [
            {
                'id': 'lote001',
                'descricao': 'Primeiro lote',
                'status': 'CRIADO',
                'criacao': '2024-01-01T10:00:00Z',
            },
            {
                'id': 'lote002',
                'descricao': 'Segundo lote',
                'status': 'EM_PROCESSAMENTO',
                'criacao': '2024-01-02T10:00:00Z',
            },
        ],
    }

    dummy_bank_pix_api.session.request.return_value = make_response(
        200, expected_response
    )

    inicio = '2024-01-01T00:00:00Z'
    fim = '2024-01-31T23:59:59Z'
    pagina_atual = 0
    itens_por_pagina = 10

    result = dummy_bank_pix_api.listar_lotes_cobv(
        inicio=inicio,
        fim=fim,
        pagina_atual=pagina_atual,
        itens_por_pagina=itens_por_pagina,
    )

    assert result == expected_response
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert args[1].endswith('/lotecobv')
    assert kwargs['params']['inicio'] == inicio
    assert kwargs['params']['fim'] == fim
    assert kwargs['params']['paginacao.paginaAtual'] == str(pagina_atual)
    assert kwargs['params']['paginacao.itensPorPagina'] == str(itens_por_pagina)


def test_listar_lotes_cobv_sem_paginacao(
    dummy_bank_pix_api: DummyBankPixAPIBase,
) -> None:
    """Testa a listagem de lotes sem parâmetros de paginação."""
    expected_response = {
        'parametros': {
            'inicio': '2024-01-01T00:00:00Z',
            'fim': '2024-01-31T23:59:59Z',
        },
        'lotes': [],
    }

    dummy_bank_pix_api.session.request.return_value = make_response(
        200, expected_response
    )

    inicio = '2024-01-01T00:00:00Z'
    fim = '2024-01-31T23:59:59Z'

    result = dummy_bank_pix_api.listar_lotes_cobv(inicio=inicio, fim=fim)

    assert result == expected_response
    dummy_bank_pix_api.session.request.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.request.call_args
    assert args[1].endswith('/lotecobv')
    assert kwargs['params']['inicio'] == inicio
    assert kwargs['params']['fim'] == fim
    # Verifica que parâmetros de paginação não foram incluídos
    assert 'paginacao.paginaAtual' not in kwargs['params']
    assert 'paginacao.itensPorPagina' not in kwargs['params']


def test_criar_lote_cobv_com_erro_400(dummy_bank_pix_api: DummyBankPixAPIBase) -> None:
    """Testa tratamento de erro 400 ao criar lote."""
    dummy_bank_pix_api.session.request.return_value = make_response(
        400,
        {
            'type': 'https://pix.bcb.gov.br/api/v2/error/LoteCobVOperacaoInvalida',
            'title': 'Lote de cobranças inválido',
            'status': 400,
            'detail': 'O objeto loteCobV.cobsV não respeita o schema.',
            'violacoes': [
                {
                    'razao': 'O objeto loteCobV.cobsV não respeita o schema.',
                    'propriedade': 'loteCobV.cobsV',
                }
            ],
        },
    )

    with pytest.raises(PixErroValidacaoException) as exc_info:
        dummy_bank_pix_api.criar_lote_cobv(
            'lote123', {'descricao': 'Teste', 'cobsv': []}
        )

    assert exc_info.value.status == 400
    assert 'loteCobV.cobsV' in exc_info.value.detail


def test_consultar_lote_cobv_com_erro_404(
    dummy_bank_pix_api: DummyBankPixAPIBase,
) -> None:
    """Testa tratamento de erro 404 ao consultar lote."""
    dummy_bank_pix_api.session.request.return_value = make_response(
        404,
        {
            'type': 'https://pix.bcb.gov.br/api/v2/error/LoteCobVNaoEncontrado',
            'title': 'Lote não encontrado',
            'status': 404,
            'detail': 'Lote não encontrado para o id informado.',
        },
    )

    with pytest.raises(PixRecursoNaoEncontradoException):
        dummy_bank_pix_api.consultar_lote_cobv('lote_inexistente')


def test_alterar_lote_cobv_com_erro_403(
    dummy_bank_pix_api: DummyBankPixAPIBase,
) -> None:
    """Testa tratamento de erro 403 ao alterar lote."""
    dummy_bank_pix_api.session.request.return_value = make_response(
        403,
        {
            'type': 'https://pix.bcb.gov.br/api/v2/error/AcessoNegado',
            'title': 'Acesso Negado',
            'status': 403,
            'detail': 'Requisição de participante autenticado que viola regra de autorização.',
        },
    )

    with pytest.raises(PixAcessoNegadoException):
        dummy_bank_pix_api.alterar_lote_cobv('lote123', {'descricao': 'Teste'})


def test_listar_lotes_cobv_com_erro_503(
    dummy_bank_pix_api: DummyBankPixAPIBase,
) -> None:
    """Testa tratamento de erro 503 ao listar lotes."""
    dummy_bank_pix_api.session.request.return_value = make_response(
        503,
        {
            'type': 'https://pix.bcb.gov.br/api/v2/error/ServicoIndisponivel',
            'title': 'Serviço Indisponível',
            'status': 503,
            'detail': 'Serviço não está disponível no momento.',
        },
    )

    with pytest.raises(PixErroServicoIndisponivelException):
        dummy_bank_pix_api.listar_lotes_cobv(
            inicio='2024-01-01T00:00:00Z', fim='2024-01-31T23:59:59Z'
        )
