"""Configuração compartilhada para testes do pypix-api."""

import json
import os
from collections.abc import Generator
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests

from pypix_api.http import DEFAULT_TIMEOUT


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


def make_response(
    status_code: int,
    json_body: Any | None = None,
    content_type: str = 'application/json',
    content: bytes | None = None,
) -> requests.Response:
    """Monta um ``requests.Response`` real.

    Usado no lugar de ``Mock`` sempre que o teste precisar passar pelo
    ``_handle_error_response``: com um mock, o handler recebia um objeto que não
    se comporta como resposta HTTP e o tratamento de erro nunca era exercitado.
    """
    response = requests.Response()
    response.status_code = status_code
    if content is not None:
        response._content = content
    elif json_body is not None:
        # ensure_ascii=False para que o corpo tenha acentuação real, como a de
        # um PSP — o texto cru é preservado em `detail` quando o formato não é
        # o do BACEN, e o escape \uXXXX mascararia isso nos testes
        response._content = json.dumps(json_body, ensure_ascii=False).encode()
    else:
        response._content = b''
    if content_type:
        response.headers['Content-Type'] = content_type
    return response


def assert_requisicao(
    session: Mock,
    metodo: str,
    url: str,
    *,
    timeout: Any = DEFAULT_TIMEOUT,
    **kwargs_esperados: Any,
) -> None:
    """Confere a única requisição feita na sessão mockada.

    Verifica verbo, URL, os kwargs informados e — sempre — que a requisição
    levou timeout. Os headers não são conferidos aqui: são montados pelo
    ``_request`` e testados em ``test_request_base``.
    """
    session.request.assert_called_once()
    args, kwargs = session.request.call_args
    assert args[0] == metodo
    assert args[1] == url
    assert kwargs['timeout'] == timeout
    for chave, esperado in kwargs_esperados.items():
        assert kwargs[chave] == esperado


@pytest.fixture
def mock_session() -> Mock:
    """Fixture que retorna uma sessão HTTP mockada."""
    session = Mock(spec=requests.Session)

    # Mock response padrão
    mock_response = make_response(200, {'success': True, 'data': {}})

    # Toda saída HTTP da biblioteca passa por session.request
    session.request.return_value = mock_response
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
def mock_error_response() -> requests.Response:
    """Resposta 400 real, para exercitar o tratamento de erro."""
    return make_response(
        400,
        {
            'type': 'ErroValidacao',
            'title': 'Erro de validação',
            'status': 400,
            'detail': 'Dados inválidos fornecidos',
        },
    )


@pytest.fixture
def mock_unauthorized_response() -> requests.Response:
    """Resposta 403 real, para exercitar o tratamento de erro."""
    return make_response(
        403,
        {
            'type': 'AcessoNegado',
            'title': 'Acesso negado',
            'status': 403,
            'detail': 'Token inválido ou expirado',
        },
    )


@pytest.fixture
def mock_not_found_response() -> requests.Response:
    """Resposta 404 real, para exercitar o tratamento de erro."""
    return make_response(
        404,
        {
            'type': 'RecursoNaoEncontrado',
            'title': 'Recurso não encontrado',
            'status': 404,
            'detail': 'O recurso solicitado não foi encontrado',
        },
    )


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
