"""
Testes unitários para os métodos PIX da classe BankPixAPIBase usando mocks.
"""

from unittest.mock import Mock

import pytest
import requests

from pypix_api.banks.base import BankPixAPIBase
from pypix_api.banks.exceptions import PixRecursoNaoEncontradoException
from tests.conftest import assert_requisicao, make_response


class MockPixAPI(BankPixAPIBase):
    """Banco fictício para exercitar os métodos PIX.

    Herda de ``BankPixAPIBase`` para usar o ``_request`` e o
    ``_handle_error_response`` reais — só os headers são fixos, para manter as
    asserções legíveis.
    """

    BASE_URL = 'https://api.mock.com/v1'
    TOKEN_URL = 'https://api.mock.com/token'

    def __init__(self) -> None:
        super().__init__(oauth=Mock(session=Mock(), client_id='mock_client'))

    def _create_headers(self) -> dict:
        return {'Authorization': 'Bearer mock_token'}

    def get_base_url(self) -> str:
        return self.BASE_URL


@pytest.fixture
def mock_pix_api() -> MockPixAPI:
    """Fixture que retorna uma instância mock da API PIX."""
    return MockPixAPI()


@pytest.fixture
def mock_response() -> requests.Response:
    """Resposta 200 real com corpo genérico."""
    return make_response(200, {'mock': 'data'})


class TestConsultarPix:
    """Testes para o método consultar_pix."""

    def test_consultar_pix_parametros_obrigatorios(self, mock_pix_api, mock_response):
        """Testa consulta PIX com apenas parâmetros obrigatórios."""
        mock_pix_api.session.request.return_value = mock_response

        resultado = mock_pix_api.consultar_pix(
            inicio='2024-01-01T00:00:00Z', fim='2024-01-31T23:59:59Z'
        )

        assert_requisicao(
            mock_pix_api.session,
            'GET',
            'https://api.mock.com/v1/pix',
            params={'inicio': '2024-01-01T00:00:00Z', 'fim': '2024-01-31T23:59:59Z'},
        )
        assert resultado == {'mock': 'data'}

    def test_consultar_pix_todos_parametros(self, mock_pix_api, mock_response):
        """Testa consulta PIX com todos os parâmetros opcionais."""
        mock_pix_api.session.request.return_value = mock_response

        resultado = mock_pix_api.consultar_pix(
            inicio='2024-01-01T00:00:00Z',
            fim='2024-01-31T23:59:59Z',
            txid='txid123',
            txid_presente=True,
            devolucao_presente=False,
            cpf='12345678909',
            pagina_atual=1,
            itens_por_pagina=50,
        )

        expected_params = {
            'inicio': '2024-01-01T00:00:00Z',
            'fim': '2024-01-31T23:59:59Z',
            'txid': 'txid123',
            'txIdPresente': 'true',
            'devolucaoPresente': 'false',
            'cpf': '12345678909',
            'paginacao.paginaAtual': '1',
            'paginacao.itensPorPagina': '50',
        }

        assert_requisicao(
            mock_pix_api.session,
            'GET',
            'https://api.mock.com/v1/pix',
            params=expected_params,
        )
        assert resultado == {'mock': 'data'}

    def test_consultar_pix_com_cnpj(self, mock_pix_api, mock_response):
        """Testa consulta PIX com CNPJ."""
        mock_pix_api.session.request.return_value = mock_response

        resultado = mock_pix_api.consultar_pix(
            inicio='2024-01-01T00:00:00Z',
            fim='2024-01-31T23:59:59Z',
            cnpj='12345678000195',
        )

        expected_params = {
            'inicio': '2024-01-01T00:00:00Z',
            'fim': '2024-01-31T23:59:59Z',
            'cnpj': '12345678000195',
        }

        assert_requisicao(
            mock_pix_api.session,
            'GET',
            'https://api.mock.com/v1/pix',
            params=expected_params,
        )
        assert resultado == {'mock': 'data'}

    def test_consultar_pix_cpf_cnpj_simultaneos_erro(self, mock_pix_api):
        """Testa erro ao usar CPF e CNPJ simultaneamente."""
        with pytest.raises(
            ValueError, match='CPF e CNPJ não podem ser utilizados simultaneamente'
        ):
            mock_pix_api.consultar_pix(
                inicio='2024-01-01T00:00:00Z',
                fim='2024-01-31T23:59:59Z',
                cpf='12345678909',
                cnpj='12345678000195',
            )

    def test_consultar_pix_parametros_opcionais_none(self, mock_pix_api, mock_response):
        """Testa que parâmetros None não são incluídos na requisição."""
        mock_pix_api.session.request.return_value = mock_response

        resultado = mock_pix_api.consultar_pix(
            inicio='2024-01-01T00:00:00Z',
            fim='2024-01-31T23:59:59Z',
            txid=None,
            cpf=None,
            pagina_atual=None,
        )

        expected_params = {
            'inicio': '2024-01-01T00:00:00Z',
            'fim': '2024-01-31T23:59:59Z',
        }

        assert_requisicao(
            mock_pix_api.session,
            'GET',
            'https://api.mock.com/v1/pix',
            params=expected_params,
        )
        assert resultado == {'mock': 'data'}


class TestConsultarPixPorE2eid:
    """Testes para o método consultar_pix_por_e2eid."""

    def test_consultar_pix_por_e2eid_sucesso(self, mock_pix_api, mock_response):
        """Testa consulta PIX por e2eid com sucesso."""
        mock_pix_api.session.request.return_value = make_response(
            200,
            {
                'endToEndId': 'E12345678202301011200abcdef123456',
                'valor': '100.00',
            },
        )

        e2eid = 'E12345678202301011200abcdef123456'
        resultado = mock_pix_api.consultar_pix_por_e2eid(e2eid)

        assert_requisicao(
            mock_pix_api.session,
            'GET',
            f'https://api.mock.com/v1/pix/{e2eid}',
        )
        assert resultado['endToEndId'] == e2eid
        assert resultado['valor'] == '100.00'

    def test_consultar_pix_por_e2eid_erro_404(self, mock_pix_api):
        """Testa erro 404 ao consultar PIX inexistente."""
        mock_pix_api.session.request.return_value = make_response(
            404,
            {
                'type': 'RecursoNaoEncontrado',
                'title': 'Pix não encontrado',
                'status': 404,
                'detail': 'Não foi encontrado Pix para o EndToEndId informado',
            },
        )

        e2eid = 'E99999999999999999999999999999999'

        with pytest.raises(PixRecursoNaoEncontradoException) as exc_info:
            mock_pix_api.consultar_pix_por_e2eid(e2eid)

        assert exc_info.value.status == 404
        assert 'EndToEndId' in exc_info.value.detail


class TestSolicitarDevolucaoPix:
    """Testes para o método solicitar_devolucao_pix."""

    def test_solicitar_devolucao_pix_sucesso(self, mock_pix_api, mock_response):
        """Testa solicitação de devolução PIX com sucesso."""
        mock_pix_api.session.request.return_value = make_response(
            200,
            {
                'id': 'devolucao123',
                'valor': '50.00',
                'status': 'EM_PROCESSAMENTO',
            },
        )

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao123'
        body = {
            'valor': '50.00',
            'natureza': 'ORIGINAL',
            'descricao': 'Devolução teste',
        }

        resultado = mock_pix_api.solicitar_devolucao_pix(e2eid, id_devolucao, body)

        assert_requisicao(
            mock_pix_api.session,
            'PUT',
            f'https://api.mock.com/v1/pix/{e2eid}/devolucao/{id_devolucao}',
            json=body,
        )
        assert resultado['id'] == 'devolucao123'
        assert resultado['valor'] == '50.00'
        assert resultado['status'] == 'EM_PROCESSAMENTO'

    def test_solicitar_devolucao_pix_natureza_retirada(
        self, mock_pix_api, mock_response
    ):
        """Testa solicitação de devolução PIX com natureza RETIRADA."""
        mock_pix_api.session.request.return_value = make_response(
            200,
            {
                'id': 'devolucao456',
                'valor': '25.00',
                'natureza': 'RETIRADA',
                'status': 'EM_PROCESSAMENTO',
            },
        )

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao456'
        body = {
            'valor': '25.00',
            'natureza': 'RETIRADA',
            'descricao': 'Devolução de troco',
        }

        resultado = mock_pix_api.solicitar_devolucao_pix(e2eid, id_devolucao, body)

        assert_requisicao(
            mock_pix_api.session,
            'PUT',
            f'https://api.mock.com/v1/pix/{e2eid}/devolucao/{id_devolucao}',
            json=body,
        )
        assert resultado['natureza'] == 'RETIRADA'

    def test_solicitar_devolucao_pix_sem_descricao(self, mock_pix_api, mock_response):
        """Testa solicitação de devolução PIX sem descrição."""
        mock_pix_api.session.request.return_value = make_response(
            200,
            {
                'id': 'devolucao789',
                'valor': '10.00',
                'status': 'EM_PROCESSAMENTO',
            },
        )

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao789'
        body = {'valor': '10.00'}

        resultado = mock_pix_api.solicitar_devolucao_pix(e2eid, id_devolucao, body)

        assert_requisicao(
            mock_pix_api.session,
            'PUT',
            f'https://api.mock.com/v1/pix/{e2eid}/devolucao/{id_devolucao}',
            json=body,
        )
        assert resultado['id'] == 'devolucao789'


class TestConsultarDevolucaoPix:
    """Testes para o método consultar_devolucao_pix."""

    def test_consultar_devolucao_pix_sucesso(self, mock_pix_api, mock_response):
        """Testa consulta de devolução PIX com sucesso."""
        mock_pix_api.session.request.return_value = make_response(
            200,
            {
                'id': 'devolucao123',
                'valor': '50.00',
                'status': 'DEVOLVIDO',
                'natureza': 'ORIGINAL',
                'descricao': 'Devolução processada',
            },
        )

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao123'

        resultado = mock_pix_api.consultar_devolucao_pix(e2eid, id_devolucao)

        assert_requisicao(
            mock_pix_api.session,
            'GET',
            f'https://api.mock.com/v1/pix/{e2eid}/devolucao/{id_devolucao}',
        )
        assert resultado['id'] == 'devolucao123'
        assert resultado['status'] == 'DEVOLVIDO'
        assert resultado['valor'] == '50.00'

    def test_consultar_devolucao_pix_em_processamento(
        self, mock_pix_api, mock_response
    ):
        """Testa consulta de devolução PIX em processamento."""
        mock_pix_api.session.request.return_value = make_response(
            200,
            {
                'id': 'devolucao456',
                'valor': '25.00',
                'status': 'EM_PROCESSAMENTO',
                'natureza': 'RETIRADA',
            },
        )

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao456'

        resultado = mock_pix_api.consultar_devolucao_pix(e2eid, id_devolucao)

        assert_requisicao(
            mock_pix_api.session,
            'GET',
            f'https://api.mock.com/v1/pix/{e2eid}/devolucao/{id_devolucao}',
        )
        assert resultado['id'] == 'devolucao456'
        assert resultado['status'] == 'EM_PROCESSAMENTO'
        assert resultado['valor'] == '25.00'
        assert resultado['natureza'] == 'RETIRADA'

    def test_consultar_devolucao_pix_nao_encontrada(self, mock_pix_api):
        """Testa erro ao consultar devolução inexistente."""
        mock_pix_api.session.request.return_value = make_response(
            404,
            {
                'type': 'RecursoNaoEncontrado',
                'title': 'Devolução não encontrada',
                'status': 404,
                'detail': 'Não foi encontrada devolução com o id informado',
            },
        )

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao_inexistente'

        with pytest.raises(
            PixRecursoNaoEncontradoException, match='Devolução não encontrada'
        ):
            mock_pix_api.consultar_devolucao_pix(e2eid, id_devolucao)

    def test_consultar_devolucao_pix_rejeitada(self, mock_pix_api, mock_response):
        """Testa consulta de devolução PIX rejeitada."""
        mock_pix_api.session.request.return_value = make_response(
            200,
            {
                'id': 'devolucao789',
                'valor': '100.00',
                'status': 'NAO_REALIZADO',
                'natureza': 'ORIGINAL',
                'motivo': 'Valor excede limite permitido',
            },
        )

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao789'

        resultado = mock_pix_api.consultar_devolucao_pix(e2eid, id_devolucao)

        assert_requisicao(
            mock_pix_api.session,
            'GET',
            f'https://api.mock.com/v1/pix/{e2eid}/devolucao/{id_devolucao}',
        )
        assert resultado['id'] == 'devolucao789'
        assert resultado['status'] == 'NAO_REALIZADO'
        assert resultado['motivo'] == 'Valor excede limite permitido'


class TestPixMethodsIntegracao:
    """Testes de integração entre os métodos PIX."""

    def test_fluxo_completo_devolucao(self, mock_pix_api):
        """Testa fluxo completo: consultar PIX -> solicitar devolução -> consultar devolução."""
        mock_response_pix = make_response(
            200,
            {
                'endToEndId': 'E12345678202301011200abcdef123456',
                'valor': '100.00',
                'status': 'CONCLUIDA',
            },
        )
        mock_response_devolucao = make_response(
            200,
            {'id': 'devolucao123', 'valor': '50.00', 'status': 'EM_PROCESSAMENTO'},
        )
        mock_response_consulta = make_response(
            200,
            {'id': 'devolucao123', 'valor': '50.00', 'status': 'DEVOLVIDO'},
        )

        # Uma resposta por chamada, na ordem do fluxo
        mock_pix_api.session.request.side_effect = [
            mock_response_pix,
            mock_response_devolucao,
            mock_response_consulta,
        ]

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao123'

        # 1. Consultar PIX
        pix = mock_pix_api.consultar_pix_por_e2eid(e2eid)
        assert pix['endToEndId'] == e2eid
        assert pix['valor'] == '100.00'

        # 2. Solicitar devolução
        body_devolucao = {
            'valor': '50.00',
            'natureza': 'ORIGINAL',
            'descricao': 'Devolução parcial',
        }
        devolucao = mock_pix_api.solicitar_devolucao_pix(
            e2eid, id_devolucao, body_devolucao
        )
        assert devolucao['id'] == id_devolucao
        assert devolucao['status'] == 'EM_PROCESSAMENTO'

        # 3. Consultar devolução
        consulta_devolucao = mock_pix_api.consultar_devolucao_pix(e2eid, id_devolucao)
        assert consulta_devolucao['id'] == id_devolucao
        assert consulta_devolucao['status'] == 'DEVOLVIDO'

        # Verificar chamadas: dois GET (consultas) e um PUT (devolução)
        verbos = [
            chamada.args[0] for chamada in mock_pix_api.session.request.call_args_list
        ]
        assert verbos == ['GET', 'PUT', 'GET']
