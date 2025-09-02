"""
Testes unitários para os métodos PIX da classe BankPixAPIBase usando mocks.
"""

from unittest.mock import Mock

import pytest
from requests import Response

from pypix_api.banks.methods.pix_methods import PixMethods


class MockPixAPI(PixMethods):
    """Classe mock que herda de PixMethods para testes."""

    def __init__(self) -> None:
        self.session = Mock()

    def _create_headers(self) -> dict:
        return {'Authorization': 'Bearer mock_token'}

    def get_base_url(self) -> str:
        return 'https://api.mock.com/v1'

    def _handle_error_response(self, response: Response) -> None:
        if not response.ok:
            response.raise_for_status()


@pytest.fixture
def mock_pix_api() -> MockPixAPI:
    """Fixture que retorna uma instância mock da API PIX."""
    return MockPixAPI()


@pytest.fixture
def mock_response() -> Mock:
    """Fixture que retorna um mock de resposta HTTP."""
    response = Mock(spec=Response)
    response.ok = True
    response.json.return_value = {'mock': 'data'}
    return response


class TestConsultarPix:
    """Testes para o método consultar_pix."""

    def test_consultar_pix_parametros_obrigatorios(self, mock_pix_api, mock_response):
        """Testa consulta PIX com apenas parâmetros obrigatórios."""
        mock_pix_api.session.get.return_value = mock_response

        resultado = mock_pix_api.consultar_pix(
            inicio='2024-01-01T00:00:00Z', fim='2024-01-31T23:59:59Z'
        )

        mock_pix_api.session.get.assert_called_once_with(
            'https://api.mock.com/v1/pix',
            headers={'Authorization': 'Bearer mock_token'},
            params={'inicio': '2024-01-01T00:00:00Z', 'fim': '2024-01-31T23:59:59Z'},
        )
        assert resultado == {'mock': 'data'}

    def test_consultar_pix_todos_parametros(self, mock_pix_api, mock_response):
        """Testa consulta PIX com todos os parâmetros opcionais."""
        mock_pix_api.session.get.return_value = mock_response

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

        mock_pix_api.session.get.assert_called_once_with(
            'https://api.mock.com/v1/pix',
            headers={'Authorization': 'Bearer mock_token'},
            params=expected_params,
        )
        assert resultado == {'mock': 'data'}

    def test_consultar_pix_com_cnpj(self, mock_pix_api, mock_response):
        """Testa consulta PIX com CNPJ."""
        mock_pix_api.session.get.return_value = mock_response

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

        mock_pix_api.session.get.assert_called_once_with(
            'https://api.mock.com/v1/pix',
            headers={'Authorization': 'Bearer mock_token'},
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
        mock_pix_api.session.get.return_value = mock_response

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

        mock_pix_api.session.get.assert_called_once_with(
            'https://api.mock.com/v1/pix',
            headers={'Authorization': 'Bearer mock_token'},
            params=expected_params,
        )
        assert resultado == {'mock': 'data'}


class TestConsultarPixPorE2eid:
    """Testes para o método consultar_pix_por_e2eid."""

    def test_consultar_pix_por_e2eid_sucesso(self, mock_pix_api, mock_response):
        """Testa consulta PIX por e2eid com sucesso."""
        mock_response.json.return_value = {
            'endToEndId': 'E12345678202301011200abcdef123456',
            'valor': '100.00',
        }
        mock_pix_api.session.get.return_value = mock_response

        e2eid = 'E12345678202301011200abcdef123456'
        resultado = mock_pix_api.consultar_pix_por_e2eid(e2eid)

        mock_pix_api.session.get.assert_called_once_with(
            f'https://api.mock.com/v1/pix/{e2eid}',
            headers={'Authorization': 'Bearer mock_token'},
        )
        assert resultado['endToEndId'] == e2eid
        assert resultado['valor'] == '100.00'

    def test_consultar_pix_por_e2eid_erro_404(self, mock_pix_api):
        """Testa erro 404 ao consultar PIX inexistente."""
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 404
        mock_pix_api.session.get.return_value = mock_response

        # Mock do método _handle_error_response para simular o comportamento real
        def mock_handle_error(response):
            if response.status_code == 404:
                raise Exception('PIX não encontrado')

        mock_pix_api._handle_error_response = mock_handle_error

        e2eid = 'E99999999999999999999999999999999'

        with pytest.raises(Exception, match='PIX não encontrado'):
            mock_pix_api.consultar_pix_por_e2eid(e2eid)


class TestSolicitarDevolucaoPix:
    """Testes para o método solicitar_devolucao_pix."""

    def test_solicitar_devolucao_pix_sucesso(self, mock_pix_api, mock_response):
        """Testa solicitação de devolução PIX com sucesso."""
        mock_response.json.return_value = {
            'id': 'devolucao123',
            'valor': '50.00',
            'status': 'EM_PROCESSAMENTO',
        }
        mock_pix_api.session.put.return_value = mock_response

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao123'
        body = {
            'valor': '50.00',
            'natureza': 'ORIGINAL',
            'descricao': 'Devolução teste',
        }

        resultado = mock_pix_api.solicitar_devolucao_pix(e2eid, id_devolucao, body)

        mock_pix_api.session.put.assert_called_once_with(
            f'https://api.mock.com/v1/pix/{e2eid}/devolucao/{id_devolucao}',
            headers={'Authorization': 'Bearer mock_token'},
            json=body,
        )
        assert resultado['id'] == 'devolucao123'
        assert resultado['valor'] == '50.00'
        assert resultado['status'] == 'EM_PROCESSAMENTO'

    def test_solicitar_devolucao_pix_natureza_retirada(
        self, mock_pix_api, mock_response
    ):
        """Testa solicitação de devolução PIX com natureza RETIRADA."""
        mock_response.json.return_value = {
            'id': 'devolucao456',
            'valor': '25.00',
            'natureza': 'RETIRADA',
            'status': 'EM_PROCESSAMENTO',
        }
        mock_pix_api.session.put.return_value = mock_response

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao456'
        body = {
            'valor': '25.00',
            'natureza': 'RETIRADA',
            'descricao': 'Devolução de troco',
        }

        resultado = mock_pix_api.solicitar_devolucao_pix(e2eid, id_devolucao, body)

        mock_pix_api.session.put.assert_called_once_with(
            f'https://api.mock.com/v1/pix/{e2eid}/devolucao/{id_devolucao}',
            headers={'Authorization': 'Bearer mock_token'},
            json=body,
        )
        assert resultado['natureza'] == 'RETIRADA'

    def test_solicitar_devolucao_pix_sem_descricao(self, mock_pix_api, mock_response):
        """Testa solicitação de devolução PIX sem descrição."""
        mock_response.json.return_value = {
            'id': 'devolucao789',
            'valor': '10.00',
            'status': 'EM_PROCESSAMENTO',
        }
        mock_pix_api.session.put.return_value = mock_response

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao789'
        body = {'valor': '10.00'}

        resultado = mock_pix_api.solicitar_devolucao_pix(e2eid, id_devolucao, body)

        mock_pix_api.session.put.assert_called_once_with(
            f'https://api.mock.com/v1/pix/{e2eid}/devolucao/{id_devolucao}',
            headers={'Authorization': 'Bearer mock_token'},
            json=body,
        )
        assert resultado['id'] == 'devolucao789'


class TestConsultarDevolucaoPix:
    """Testes para o método consultar_devolucao_pix."""

    def test_consultar_devolucao_pix_sucesso(self, mock_pix_api, mock_response):
        """Testa consulta de devolução PIX com sucesso."""
        mock_response.json.return_value = {
            'id': 'devolucao123',
            'valor': '50.00',
            'status': 'DEVOLVIDO',
            'natureza': 'ORIGINAL',
            'descricao': 'Devolução processada',
        }
        mock_pix_api.session.get.return_value = mock_response

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao123'

        resultado = mock_pix_api.consultar_devolucao_pix(e2eid, id_devolucao)

        mock_pix_api.session.get.assert_called_once_with(
            f'https://api.mock.com/v1/pix/{e2eid}/devolucao/{id_devolucao}',
            headers={'Authorization': 'Bearer mock_token'},
        )
        assert resultado['id'] == 'devolucao123'
        assert resultado['status'] == 'DEVOLVIDO'
        assert resultado['valor'] == '50.00'

    def test_consultar_devolucao_pix_em_processamento(
        self, mock_pix_api, mock_response
    ):
        """Testa consulta de devolução PIX em processamento."""
        mock_response.json.return_value = {
            'id': 'devolucao456',
            'valor': '25.00',
            'status': 'EM_PROCESSAMENTO',
            'natureza': 'RETIRADA',
        }
        mock_pix_api.session.get.return_value = mock_response

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao456'

        resultado = mock_pix_api.consultar_devolucao_pix(e2eid, id_devolucao)

        mock_pix_api.session.get.assert_called_once_with(
            f'https://api.mock.com/v1/pix/{e2eid}/devolucao/{id_devolucao}',
            headers={'Authorization': 'Bearer mock_token'},
        )
        assert resultado['id'] == 'devolucao456'
        assert resultado['status'] == 'EM_PROCESSAMENTO'
        assert resultado['valor'] == '25.00'
        assert resultado['natureza'] == 'RETIRADA'

    def test_consultar_devolucao_pix_nao_encontrada(self, mock_pix_api):
        """Testa erro ao consultar devolução inexistente."""
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 404
        mock_pix_api.session.get.return_value = mock_response

        # Mock do método _handle_error_response para simular o comportamento real
        def mock_handle_error(response):
            if response.status_code == 404:
                raise Exception('Devolução não encontrada')

        mock_pix_api._handle_error_response = mock_handle_error

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao_inexistente'

        with pytest.raises(Exception, match='Devolução não encontrada'):
            mock_pix_api.consultar_devolucao_pix(e2eid, id_devolucao)

    def test_consultar_devolucao_pix_rejeitada(self, mock_pix_api, mock_response):
        """Testa consulta de devolução PIX rejeitada."""
        mock_response.json.return_value = {
            'id': 'devolucao789',
            'valor': '100.00',
            'status': 'NAO_REALIZADO',
            'natureza': 'ORIGINAL',
            'motivo': 'Valor excede limite permitido',
        }
        mock_pix_api.session.get.return_value = mock_response

        e2eid = 'E12345678202301011200abcdef123456'
        id_devolucao = 'devolucao789'

        resultado = mock_pix_api.consultar_devolucao_pix(e2eid, id_devolucao)

        mock_pix_api.session.get.assert_called_once_with(
            f'https://api.mock.com/v1/pix/{e2eid}/devolucao/{id_devolucao}',
            headers={'Authorization': 'Bearer mock_token'},
        )
        assert resultado['id'] == 'devolucao789'
        assert resultado['status'] == 'NAO_REALIZADO'
        assert resultado['motivo'] == 'Valor excede limite permitido'


class TestPixMethodsIntegracao:
    """Testes de integração entre os métodos PIX."""

    def test_fluxo_completo_devolucao(self, mock_pix_api):
        """Testa fluxo completo: consultar PIX -> solicitar devolução -> consultar devolução."""
        # Mock para consulta do PIX
        mock_response_pix = Mock(spec=Response)
        mock_response_pix.ok = True
        mock_response_pix.json.return_value = {
            'endToEndId': 'E12345678202301011200abcdef123456',
            'valor': '100.00',
            'status': 'CONCLUIDA',
        }

        # Mock para solicitação de devolução
        mock_response_devolucao = Mock(spec=Response)
        mock_response_devolucao.ok = True
        mock_response_devolucao.json.return_value = {
            'id': 'devolucao123',
            'valor': '50.00',
            'status': 'EM_PROCESSAMENTO',
        }

        # Mock para consulta da devolução
        mock_response_consulta = Mock(spec=Response)
        mock_response_consulta.ok = True
        mock_response_consulta.json.return_value = {
            'id': 'devolucao123',
            'valor': '50.00',
            'status': 'DEVOLVIDO',
        }

        # Configurar mocks para cada chamada
        mock_pix_api.session.get.side_effect = [
            mock_response_pix,
            mock_response_consulta,
        ]
        mock_pix_api.session.put.return_value = mock_response_devolucao

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

        # Verificar chamadas
        assert mock_pix_api.session.get.call_count == 2
        assert mock_pix_api.session.put.call_count == 1
