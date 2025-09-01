# Contributing to pypix-api

Obrigado pelo seu interesse em contribuir com o pypix-api! 🚀

Este documento fornece diretrizes para contribuições ao projeto.

## Sumário

- [Como Contribuir](#como-contribuir)
- [Configurando o Ambiente de Desenvolvimento](#configurando-o-ambiente-de-desenvolvimento)
- [Processo de Desenvolvimento](#processo-de-desenvolvimento)
- [Padrões de Código](#padrões-de-código)
- [Executando Testes](#executando-testes)
- [Submitting Changes](#submitting-changes)
- [Reportando Issues](#reportando-issues)
- [Código de Conduta](#código-de-conduta)

## Como Contribuir

### Tipos de Contribuição

Aceitamos os seguintes tipos de contribuições:

- 🐛 **Bug fixes**: Correção de bugs encontrados
- ✨ **Features**: Novas funcionalidades
- 📚 **Documentation**: Melhorias na documentação
- 🧪 **Tests**: Adicionar ou melhorar testes
- 🔧 **Refactoring**: Melhorias no código sem mudanças funcionais
- 🏦 **Bank Support**: Suporte para novos bancos

### Áreas que Precisam de Ajuda

- [ ] Suporte para novos bancos (Caixa, Itaú, Santander)
- [ ] Melhorias na cobertura de testes (meta: 80%+)
- [ ] Documentação de exemplos avançados
- [ ] Performance optimization
- [ ] Async/await support
- [ ] Webhook helpers

## Configurando o Ambiente de Desenvolvimento

### Pré-requisitos

- Python 3.10+ (recomendado: 3.11 ou 3.12)
- Git
- uv (gerenciador de dependências)

### Setup Inicial

1. **Fork o repositório** no GitHub

2. **Clone seu fork**:
```bash
git clone https://github.com/SEU_USERNAME/pypix-api.git
cd pypix-api
```

3. **Configure remote upstream**:
```bash
git remote add upstream https://github.com/laddertech/pypix-api.git
```

4. **Instale uv** (se não tiver):
```bash
pip install uv
```

5. **Instale dependências**:
```bash
make sync
# ou
uv sync && uv pip install -e ".[dev]"
```

6. **Configure pre-commit hooks**:
```bash
make pre-commit-install
# ou
./scripts/setup_pre_commit.sh
```

7. **Teste a instalação**:
```bash
make test
make quality
```

### Configuração do Ambiente (Opcional)

Crie um arquivo `.env` baseado em `.env.exemplo` para testes de integração:

```bash
cp .env.exemplo .env
# Edite .env com suas credenciais de sandbox
```

## Processo de Desenvolvimento

### Branch Strategy

Usamos uma estratégia de branches baseada em Git Flow:

- `main`: Branch de produção (releases)
- `develop`: Branch de desenvolvimento (features)
- `feature/nome-da-feature`: Branches de feature
- `hotfix/nome-do-fix`: Correções urgentes

### Workflow

1. **Sincronize com upstream**:
```bash
git checkout develop
git fetch upstream
git merge upstream/develop
```

2. **Crie branch de feature**:
```bash
git checkout -b feature/minha-nova-feature
```

3. **Faça suas alterações**:
```bash
# Edite os arquivos...
git add .
git commit -m "feat: adiciona nova funcionalidade"
```

4. **Execute testes e qualidade**:
```bash
make quality-full
```

5. **Push para seu fork**:
```bash
git push origin feature/minha-nova-feature
```

6. **Abra Pull Request** no GitHub

### Convenções de Commit

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

#### Tipos de Commit

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `style`: Formatação, sem mudanças funcionais
- `refactor`: Refatoração sem mudanças funcionais
- `test`: Adicionar ou modificar testes
- `ci`: Mudanças no CI/CD
- `chore`: Manutenção geral

#### Exemplos

```bash
feat(banks): adiciona suporte para Banco Caixa
fix(auth): corrige erro de validação de certificado
docs(readme): atualiza exemplos de uso
test(pix): adiciona testes para método de devolução
ci: adiciona verificação de security scan
refactor(scopes): simplifica sistema de registry
```

## Padrões de Código

### Code Style

- **Formatter**: Ruff (configurado em `pyproject.toml`)
- **Linter**: Ruff com regras rigorosas
- **Type Checking**: MyPy habilitado
- **Line Length**: 88 caracteres
- **Quote Style**: Single quotes ('string')

### Estrutura de Arquivos

```
pypix_api/
├── auth/           # Autenticação (OAuth2, mTLS)
├── banks/          # Implementações específicas de bancos
│   ├── methods/    # Mixins com métodos da API
│   ├── bb.py       # Banco do Brasil
│   └── sicoob.py   # Sicoob
├── models/         # Modelos de dados PIX
├── scopes/         # Sistema de scopes OAuth2
└── utils/          # Utilitários gerais
```

### Convenções de Nomenclatura

- **Classes**: PascalCase (`BankPixAPI`)
- **Functions/Methods**: snake_case (`get_token`)
- **Constants**: UPPER_SNAKE_CASE (`TOKEN_URL`)
- **Private**: Prefixo underscore (`_handle_error`)

### Documentation Strings

Use docstrings estilo Google:

```python
def create_charge(self, txid: str, body: dict) -> dict:
    """Cria uma nova cobrança PIX.

    Args:
        txid: Identificador único da transação
        body: Dados da cobrança conforme especificação PIX

    Returns:
        dict: Resposta da API com dados da cobrança criada

    Raises:
        PixValidationError: Dados inválidos fornecidos
        PixAuthError: Falha na autenticação

    Example:
        >>> api = BBPixAPI(oauth=oauth_client)
        >>> charge = api.create_charge('txid123', {
        ...     'calendario': {'expiracao': 3600},
        ...     'valor': {'original': '100.00'}
        ... })
    """
```

### Type Hints

Use type hints sempre que possível:

```python
from typing import Any, Dict, List, Optional, Union

def process_response(
    self,
    response: requests.Response,
    expected_type: Optional[type] = None
) -> Dict[str, Any]:
    """Process API response with type safety."""
```

## Executando Testes

### Comandos de Teste

```bash
# Testes básicos (rápidos)
make test

# Testes com cobertura
make test-cov

# Todos os testes (incluindo integração)
make test-all

# Apenas testes unitários
make test-unit

# Apenas testes de integração (requer credenciais)
make test-integration

# Testes paralelos (mais rápido)
make test-fast
```

### Escrevendo Testes

#### Testes Unitários

Use mocks para isolar funcionalidades:

```python
def test_create_charge_success(mock_oauth2_client, sample_cob_data):
    """Test successful charge creation."""
    # Arrange
    api = BBPixAPI(oauth=mock_oauth2_client)
    mock_oauth2_client.session.post.return_value.json.return_value = {
        'txid': 'test123',
        'status': 'ATIVA'
    }

    # Act
    result = api.criar_cob('test123', sample_cob_data)

    # Assert
    assert result['txid'] == 'test123'
    assert result['status'] == 'ATIVA'
    mock_oauth2_client.session.post.assert_called_once()
```

#### Testes de Integração

Marque com `@pytest.mark.integration`:

```python
@pytest.mark.integration
def test_real_api_call():
    """Test real API integration."""
    if not os.getenv('CLIENT_ID'):
        pytest.skip('Integration credentials not available')

    # Test com API real...
```

#### Fixtures Úteis

Veja `tests/conftest.py` para fixtures disponíveis:

- `mock_oauth2_client`: Cliente OAuth2 mockado
- `sample_cob_data`: Dados de exemplo para cobrança
- `mock_bb_responses`: Respostas mockadas do BB
- `mock_error_response`: Resposta de erro mockada

## Submitting Changes

### Pull Request Checklist

Antes de abrir um PR, verifique:

- [ ] ✅ Testes passando (`make test-cov`)
- [ ] ✅ Qualidade passando (`make quality`)
- [ ] ✅ Pre-commit hooks configurados
- [ ] ✅ Documentação atualizada
- [ ] ✅ CHANGELOG.md atualizado
- [ ] ✅ Commit messages seguem padrão
- [ ] ✅ Branch atualizada com develop/main

### Template de Pull Request

```markdown
## Descrição

Breve descrição das mudanças realizadas.

## Tipo de Mudança

- [ ] 🐛 Bug fix
- [ ] ✨ Nova feature
- [ ] 📚 Documentação
- [ ] 🧪 Testes
- [ ] 🔧 Refactoring
- [ ] 🏦 Novo banco

## Como Testar

Passos para testar as mudanças:

1. Instalar dependências: `make sync`
2. Executar testes: `make test-cov`
3. Testar funcionalidade: `python exemplo.py`

## Checklist

- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] CHANGELOG.md atualizado
- [ ] Pre-commit hooks passando
```

### Review Process

1. **Automated Checks**: CI/CD executa testes e verificações
2. **Code Review**: Maintainers revisam o código
3. **Feedback**: Discussão e melhorias se necessário
4. **Approval**: PR aprovado por maintainer
5. **Merge**: Merge para branch principal

## Reportando Issues

### Bug Reports

Use o template de bug report:

```markdown
**Describe the bug**
Descrição clara e concisa do bug.

**To Reproduce**
Passos para reproduzir:
1. Configurar OAuth2 com '...'
2. Chamar método '...'
3. Ver erro

**Expected behavior**
Comportamento esperado.

**Environment:**
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.11.2]
- pypix-api: [e.g. 0.5.0]
- Bank: [e.g. Banco do Brasil]

**Additional context**
Contexto adicional, logs, screenshots.
```

### Feature Requests

Use o template de feature request:

```markdown
**Is your feature request related to a problem?**
Descrição do problema que a feature resolve.

**Describe the solution you'd like**
Solução desejada.

**Describe alternatives you've considered**
Alternativas consideradas.

**Additional context**
Contexto adicional, mockups, exemplos.
```

## Código de Conduta

### Nossos Padrões

Exemplos de comportamento que contribuem para um ambiente positivo:

- Usar linguagem acolhedora e inclusiva
- Respeitar pontos de vista e experiências diferentes
- Aceitar críticas construtivas graciosamente
- Focar no que é melhor para a comunidade
- Mostrar empatia com outros membros da comunidade

### Comportamentos Inaceitáveis

- Uso de linguagem ou imagens sexualizadas
- Trolling, comentários insultuosos/depreciativos
- Assédio público ou privado
- Publicar informações privadas de outros sem permissão
- Outras condutas inadequadas em ambiente profissional

### Enforcement

Casos de comportamento abusivo podem ser reportados para fabio@ladder.dev.br.
Todas as reclamações serão revisadas e investigadas.

## Getting Help

### Canais de Comunicação

- 🐛 **Issues**: Para bugs e feature requests
- 💬 **Discussions**: Para dúvidas e discussões gerais
- 📧 **Email**: fabio@ladder.dev.br para questões específicas

### Recursos Úteis

- [Documentação do PIX](https://www.bcb.gov.br/estabilidadefinanceira/pix)
- [Especificação OpenAPI](./openapi.yaml)
- [Guia de CI/CD](./docs/CI_CD_GUIDE.md)
- [Guia de Testes](./docs/TESTING_COVERAGE_GUIDE.md)
- [Guia de Type Checking](./docs/TYPE_CHECKING_GUIDE.md)

---

## Reconhecimentos

Obrigado a todos os contribuidores que tornam este projeto possível! 🙏

Para ver a lista completa de contribuidores, visite a [página de contributors](https://github.com/laddertech/pypix-api/contributors).

---

**Happy coding! 🚀**
