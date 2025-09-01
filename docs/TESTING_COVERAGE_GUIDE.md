# Guia de Testes e Cobertura para pypix-api

## Status Atual

✅ **Implementado com sucesso!**
- Cobertura de testes configurada com pytest-cov
- Meta de cobertura: **65%** (atingida: **65.54%**)
- Fixtures compartilhadas em `tests/conftest.py`
- Comandos no Makefile para diferentes tipos de teste
- Relatórios HTML e XML configurados

## Estrutura de Testes

```
tests/
├── conftest.py                    # Fixtures compartilhadas
├── tests_mock/                    # Testes unitários com mocks
│   ├── test_auth.py
│   ├── test_bankpixapibase_*.py
│   ├── test_models.py
│   └── ...
└── tests_integration/             # Testes de integração
    ├── test_sicoob_pix_api_*.py
    └── ...
```

## Comandos de Teste

### Comandos Básicos
```bash
# Testes rápidos (apenas mock, sem cobertura)
make test

# Todos os testes (mock + integração)
make test-all

# Testes com cobertura completa
make test-cov
```

### Comandos Específicos
```bash
# Apenas testes unitários/mock
make test-unit

# Apenas testes de integração
make test-integration

# Testes paralelos (rápido)
make test-fast

# Verificar meta de cobertura
make coverage-check
```

### Relatórios de Cobertura
```bash
# Gerar relatório HTML
make coverage-report

# O relatório fica disponível em:
# coverage_html/index.html
```

## Fixtures Disponíveis

### Autenticação e Credenciais
```python
@pytest.fixture
def test_client_id() -> str:
    """Retorna client ID para testes"""

@pytest.fixture
def test_token() -> str:
    """Retorna token de acesso para testes"""

@pytest.fixture
def test_certificates() -> Dict[str, str]:
    """Retorna certificados de teste"""

@pytest.fixture
def mock_env_vars():
    """Mock de variáveis de ambiente"""
```

### HTTP e API
```python
@pytest.fixture
def mock_session() -> Mock:
    """Sessão HTTP mockada"""

@pytest.fixture
def mock_oauth2_client() -> Mock:
    """Cliente OAuth2 mockado"""

@pytest.fixture
def mock_requests_session():
    """Mock da sessão requests"""
```

### Dados de Exemplo
```python
@pytest.fixture
def sample_pix_data() -> Dict[str, Any]:
    """Dados de exemplo para PIX"""

@pytest.fixture
def sample_cob_data() -> Dict[str, Any]:
    """Dados de exemplo para cobrança"""

@pytest.fixture
def sample_cobv_data() -> Dict[str, Any]:
    """Dados de exemplo para cobrança com vencimento"""
```

### Respostas Mockadas
```python
@pytest.fixture
def mock_bb_responses() -> Dict[str, Dict[str, Any]]:
    """Respostas da API do Banco do Brasil"""

@pytest.fixture
def mock_sicoob_responses() -> Dict[str, Dict[str, Any]]:
    """Respostas da API do Sicoob"""

@pytest.fixture
def mock_error_response() -> Mock:
    """Resposta de erro 400"""

@pytest.fixture
def mock_unauthorized_response() -> Mock:
    """Resposta de erro 403"""
```

## Escrevendo Testes

### Teste Unitário Básico
```python
def test_criar_cob(mock_oauth2_client, sample_cob_data):
    """Testa criação de cobrança."""
    # Arrange
    bank_api = BankPixAPIBase(oauth=mock_oauth2_client)
    mock_oauth2_client.session.post.return_value.json.return_value = {
        "txid": "test_txid_123",
        "status": "ATIVA"
    }

    # Act
    result = bank_api.criar_cob("test_txid", sample_cob_data)

    # Assert
    assert result["txid"] == "test_txid_123"
    assert result["status"] == "ATIVA"
    mock_oauth2_client.session.post.assert_called_once()
```

### Teste com Mock de Erro
```python
def test_criar_cob_error(mock_oauth2_client, mock_error_response):
    """Testa erro na criação de cobrança."""
    # Arrange
    bank_api = BankPixAPIBase(oauth=mock_oauth2_client)
    mock_oauth2_client.session.post.return_value = mock_error_response

    # Act & Assert
    with pytest.raises(PixErroValidacaoException):
        bank_api.criar_cob("invalid_txid", {})
```

### Teste de Integração
```python
@pytest.mark.integration
def test_consultar_pix_real():
    """Teste de integração real (requer credenciais)."""
    # Pula teste se não há credenciais
    if not os.getenv("CLIENT_ID"):
        pytest.skip("Credenciais não configuradas")

    # Teste real com API
    # ...
```

## Markers de Teste

### Markers Disponíveis
- `@pytest.mark.unit`: Testes unitários
- `@pytest.mark.mock`: Testes com mocks (padrão para tests_mock/)
- `@pytest.mark.integration`: Testes de integração
- `@pytest.mark.slow`: Testes que demoram mais

### Executar por Marker
```bash
# Apenas testes unitários
pytest -m "unit or mock"

# Apenas testes de integração
pytest -m integration

# Pular testes lentos
pytest -m "not slow"
```

## Configuração de Cobertura

### Configuração Atual
```toml
[tool.coverage.run]
source = ["pypix_api"]
branch = true  # Cobertura de branch
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
    "*/build/*",
    "*/dist/*",
    "*/scripts/*",
]

[tool.coverage.report]
show_missing = true
precision = 2
skip_covered = false
```

### Exclusões de Cobertura
No código, use comentários especiais para excluir linhas:

```python
# Linha específica
def debug_function():  # pragma: no cover
    print("Debug info")

# Bloco condicional
if __name__ == "__main__":  # pragma: no cover
    main()

# Método abstrato
def abstract_method(self):
    raise NotImplementedError  # pragma: no cover
```

## Relatórios de Cobertura

### Terminal
Mostra linha por linha o que falta cobrir:
```bash
make coverage-check
```

### HTML
Relatório interativo com destaque visual:
```bash
make coverage-report
# Abra: coverage_html/index.html
```

### XML
Para integração com CI/CD:
```bash
# Arquivo gerado: coverage.xml
```

## Melhorias na Cobertura

### Áreas com Baixa Cobertura
1. **Autenticação MTLS** (21%): `pypix_api/auth/mtls.py`
2. **Métodos Webhook** (23%): `pypix_api/banks/methods/webhook_*.py`
3. **Base do BankPixAPI** (42%): `pypix_api/banks/base.py`

### Como Melhorar
1. **Adicionar testes para métodos webhook**:
   ```python
   def test_configurar_webhook(mock_oauth2_client):
       # Testar configuração de webhook
   ```

2. **Testar cenários de erro**:
   ```python
   def test_handle_error_response_403():
       # Testar tratamento de erro 403
   ```

3. **Testar inicialização**:
   ```python
   def test_bank_api_init_sandbox_mode():
       # Testar modo sandbox
   ```

## CI/CD Integration

### GitHub Actions Exemplo
```yaml
- name: Run tests with coverage
  run: |
    make test-cov

- name: Upload coverage reports
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Badges de Cobertura
```markdown
![Coverage](https://img.shields.io/badge/coverage-65%25-yellow)
```

## Troubleshooting

### Teste falha com imports
```bash
# Instalar em modo editável
pip install -e .
```

### Coverage não encontra arquivos
```bash
# Verificar se source está correto no pyproject.toml
[tool.coverage.run]
source = ["pypix_api"]  # Deve apontar para o package
```

### Testes de integração falham
```bash
# Configurar variáveis de ambiente
cp .env.exemplo .env
# Editar .env com credenciais válidas
```

### Relatório HTML não é gerado
```bash
# Instalar dependências completas
pip install -e ".[dev]"
```

## Metas e Evolução

### Meta Atual: 65% ✅
- **Atingida**: 65.54%
- **Foco**: Testes unitários com mocks

### Meta Intermediária: 75%
- Adicionar testes para webhooks
- Testar cenários de erro
- Cobrir métodos de inicialização

### Meta Avançada: 85%
- Testes de integração robustos
- Cobertura de branch completa
- Testes de performance

## Recursos Adicionais

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Próximos Passos

1. **Adicionar testes para áreas com baixa cobertura**
2. **Implementar testes de integração mais robustos**
3. **Configurar CI/CD com cobertura automática**
4. **Aumentar meta de cobertura gradualmente**
5. **Adicionar testes de performance e stress**
