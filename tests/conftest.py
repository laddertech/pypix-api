"""Configuração compartilhada para testes do pypix-api."""

import os
from collections.abc import Generator
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests


@pytest.fixture(scope='session')
def test_client_id() -> str:
    """Fixture que retorna um client ID para testes."""
    return 'test_client_id_12345'


@pytest.fixture(scope='session')
def test_token() -> str:
    """Fixture que retorna um token de teste."""
    return 'test_access_token_abc123xyz'


@pytest.fixture(scope='session')
def test_certificates() -> dict[str, str]:
    """Fixture que retorna paths de certificados de teste."""
    return {
        'cert': '/path/to/test/cert.pem',
        'pvk': '/path/to/test/private.key',
        'cert_pfx': '/path/to/test/cert.pfx',
        'pwd_pfx': 'test_password',
    }


@pytest.fixture(scope='session')
def test_env_vars(
    test_client_id: str, test_certificates: dict[str, str]
) -> dict[str, str]:
    """Fixture que retorna variáveis de ambiente para testes."""
    return {
        'CLIENT_ID': test_client_id,
        'CERT': test_certificates['cert'],
        'PVK': test_certificates['pvk'],
        'CERT_PFX': test_certificates['cert_pfx'],
        'PWD_PFX': test_certificates['pwd_pfx'],
        'SANDBOX_TOKEN': 'sandbox_test_token',
    }


@pytest.fixture
def mock_env_vars(test_env_vars: dict[str, str]) -> Generator[None, None, None]:
    """Mock das variáveis de ambiente."""
    with patch.dict(os.environ, test_env_vars, clear=False):
        yield


@pytest.fixture
def mock_session() -> Mock:
    """Fixture que retorna uma sessão HTTP mockada."""
    session = Mock(spec=requests.Session)

    # Mock response padrão
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'success': True, 'data': {}}
    mock_response.headers = {'Content-Type': 'application/json'}

    # Configura métodos HTTP
    session.get.return_value = mock_response
    session.post.return_value = mock_response
    session.put.return_value = mock_response
    session.delete.return_value = mock_response
    session.patch.return_value = mock_response

    return session


@pytest.fixture
def mock_oauth2_client(
    test_client_id: str, test_token: str, mock_session: Mock
) -> Mock:
    """Fixture que retorna um OAuth2Client mockado."""
    oauth_client = Mock()
    oauth_client.client_id = test_client_id
    oauth_client.session = mock_session
    oauth_client.get_token.return_value = test_token
    oauth_client.sandbox_mode = False

    return oauth_client


@pytest.fixture
def mock_token_response() -> dict[str, Any]:
    """Fixture que retorna uma resposta de token OAuth2."""
    return {
        'access_token': 'test_access_token_abc123',
        'token_type': 'Bearer',
        'expires_in': 3600,
        'scope': 'pix.read pix.write',
    }


@pytest.fixture
def sample_pix_data() -> dict[str, Any]:
    """Fixture com dados de exemplo para PIX."""
    return {
        'e2eid': 'E12345678202309071234567890123456',
        'txid': '7978c0c97ea847e78e8849634473c1f1',
        'valor': '123.45',
        'chave': 'user@example.com',
        'horario': '2023-09-07T14:30:00Z',
        'infoPagador': 'Pagamento de teste',
    }


@pytest.fixture
def sample_cob_data() -> dict[str, Any]:
    """Fixture com dados de exemplo para cobrança."""
    return {
        'calendario': {'expiracao': 3600},
        'devedor': {
            'cpf': '12345678909',
            'nome': 'João da Silva',
        },
        'valor': {'original': '100.00'},
        'chave': 'user@example.com',
        'solicitacaoPagador': 'Pagamento de serviços',
    }


@pytest.fixture
def sample_cobv_data() -> dict[str, Any]:
    """Fixture com dados de exemplo para cobrança com vencimento."""
    return {
        'calendario': {
            'dataDeVencimento': '2025-12-31',
            'validadeAposVencimento': 30,
        },
        'devedor': {
            'logradouro': 'Rua das Flores, 123',
            'cidade': 'São Paulo',
            'uf': 'SP',
            'cep': '01234567',
            'cpf': '12345678909',
            'nome': 'Maria Silva',
        },
        'valor': {
            'original': '250.00',
            'multa': {'modalidade': '2', 'valorPerc': '5.00'},
            'juros': {'modalidade': '2', 'valorPerc': '1.00'},
        },
        'chave': 'user@example.com',
        'solicitacaoPagador': 'Fatura mensal',
    }


@pytest.fixture
def mock_bb_responses() -> dict[str, dict[str, Any]]:
    """Fixture com respostas mockadas da API do Banco do Brasil."""
    return {
        'token': {
            'access_token': 'bb_access_token_123',
            'token_type': 'Bearer',
            'expires_in': 3600,
        },
        'cob_created': {
            'txid': 'bb_txid_123456789',
            'status': 'ATIVA',
            'calendario': {'expiracao': 3600},
            'location': 'pix.bb.com.br/qr/v2/bb_txid_123456789',
        },
        'pix_consulted': {
            'endToEndId': 'E12345678202309071234567890123456',
            'txid': 'bb_txid_123456789',
            'valor': '123.45',
            'horario': '2023-09-07T14:30:00Z',
        },
    }


@pytest.fixture
def mock_sicoob_responses() -> dict[str, dict[str, Any]]:
    """Fixture com respostas mockadas da API do Sicoob."""
    return {
        'token': {
            'access_token': 'sicoob_access_token_456',
            'token_type': 'Bearer',
            'expires_in': 3600,
        },
        'cob_created': {
            'txid': 'sicoob_txid_789012345',
            'status': 'ATIVA',
            'calendario': {'expiracao': 3600},
            'location': 'pix.sicoob.com.br/qr/v2/sicoob_txid_789012345',
        },
        'webhook_configured': {
            'webhookUrl': 'https://webhook.example.com/pix',
            'chave': 'user@example.com',
            'criacao': '2023-09-07T10:00:00Z',
        },
    }


@pytest.fixture
def mock_error_response() -> Mock:
    """Fixture que retorna uma resposta de erro mockada."""
    response = Mock()
    response.status_code = 400
    response.headers = {'Content-Type': 'application/json'}
    response.json.return_value = {
        'type': 'ErroValidacao',
        'title': 'Erro de validação',
        'status': 400,
        'detail': 'Dados inválidos fornecidos',
    }
    return response


@pytest.fixture
def mock_unauthorized_response() -> Mock:
    """Fixture que retorna uma resposta 403 mockada."""
    response = Mock()
    response.status_code = 403
    response.headers = {'Content-Type': 'application/json'}
    response.json.return_value = {
        'type': 'AcessoNegado',
        'title': 'Acesso negado',
        'status': 403,
        'detail': 'Token inválido ou expirado',
    }
    return response


@pytest.fixture
def mock_not_found_response() -> Mock:
    """Fixture que retorna uma resposta 404 mockada."""
    response = Mock()
    response.status_code = 404
    response.headers = {'Content-Type': 'application/json'}
    response.json.return_value = {
        'type': 'RecursoNaoEncontrado',
        'title': 'Recurso não encontrado',
        'status': 404,
        'detail': 'O recurso solicitado não foi encontrado',
    }
    return response


@pytest.fixture
def mock_requests_session() -> Generator[Mock, None, None]:
    """Mock da sessão requests para testes de integração."""
    with patch('requests.Session') as mock:
        session_instance = Mock()
        mock.return_value = session_instance

        # Configurar resposta padrão
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_response.headers = {'Content-Type': 'application/json'}

        session_instance.get.return_value = mock_response
        session_instance.post.return_value = mock_response
        session_instance.put.return_value = mock_response
        session_instance.delete.return_value = mock_response

        yield session_instance


@pytest.fixture(autouse=True)
def clean_coverage_artifacts():
    """Remove artefatos de cobertura antes dos testes."""
    yield
    # Cleanup após os testes se necessário
    import shutil

    try:
        if os.path.exists('coverage_html'):
            shutil.rmtree('coverage_html')
        if os.path.exists('.coverage'):
            os.remove('.coverage')
    except (OSError, PermissionError):
        pass  # Ignora erros de limpeza


# Configuração para markers
def pytest_configure(config):
    """Configuração adicional do pytest."""
    config.addinivalue_line('markers', 'unit: marca testes como testes unitários')
    config.addinivalue_line(
        'markers', 'integration: marca testes como testes de integração'
    )
    config.addinivalue_line('markers', 'mock: marca testes como testes com mock')
    config.addinivalue_line('markers', 'slow: marca testes como lentos')


def pytest_collection_modifyitems(config, items):
    """Modifica a coleta de testes para adicionar markers automáticos."""
    for item in items:
        # Adiciona marker 'unit' por padrão se não tiver outros markers
        if not any(
            mark.name in ['integration', 'mock', 'unit', 'slow']
            for mark in item.iter_markers()
        ):
            if 'tests_mock' in str(item.fspath):
                item.add_marker(pytest.mark.mock)
            elif 'tests_integration' in str(item.fspath):
                item.add_marker(pytest.mark.integration)
            else:
                item.add_marker(pytest.mark.unit)
