# Guia de CI/CD para pypix-api

## Status Atual

✅ **Implementado com sucesso!**
- Pipeline CI/CD completo com GitHub Actions
- Matriz de testes: Python 3.10, 3.11, 3.12
- Verificações de qualidade automatizadas
- Deploy automático para PyPI
- Badges no README para status visual

## Estrutura dos Workflows

```
.github/workflows/
├── ci.yml          # Pipeline de Integração Contínua
└── cd.yml          # Pipeline de Deploy Contínuo
```

## CI Pipeline (ci.yml)

### Jobs Configurados

#### 1. **Quality Checks** 🔍
```yaml
- Verificação de formatação (Ruff format)
- Linting de código (Ruff check)
- Type checking (MyPy)
- Scan de segurança (Bandit)
```

#### 2. **Test Matrix** 🧪
```yaml
Versões Python: 3.10, 3.11, 3.12
Sistemas: Ubuntu (padrão), Windows, macOS (Python 3.10)
Cobertura: Apenas Ubuntu + Python 3.10
```

#### 3. **Integration Tests** 🔗
```yaml
- Executa apenas no push para main
- Testes de integração com APIs reais
- Continue-on-error habilitado
```

#### 4. **Build Verification** 📦
```yaml
- Build do pacote Python
- Verificação com twine check
- Upload de artefatos
```

### Triggers do CI
- Push para `main` ou `develop`
- Pull Requests para `main` ou `develop`
- Trigger manual (`workflow_dispatch`)

### Otimizações
- **Concurrency control**: Cancela runs duplicados
- **Cache habilitado**: Para uv e dependências
- **Fast-fail desabilitado**: Testa todas as versões Python
- **Continue-on-error**: Para testes opcionais (bandit, integração)

## CD Pipeline (cd.yml)

### Jobs Configurados

#### 1. **Pre-deployment** ✅
```yaml
- Executa suite completa de qualidade
- Verifica consistência de versões
- Validação antes do deploy
```

#### 2. **Deploy** 🚀
```yaml
- Build e verificação do pacote
- Deploy para Test PyPI (manual)
- Deploy para PyPI (release)
- Trusted publishing habilitado
```

#### 3. **Verification** ✔️
```yaml
- Aguarda disponibilidade no PyPI
- Testa instalação do pacote
- Smoke tests básicos
```

#### 4. **Release Notes** 📝
```yaml
- Geração automática de changelog
- Atualização de release notes
- Links para comparação de commits
```

### Triggers do CD
- Release publicado (automático)
- Trigger manual com versão especificada

## Badges Implementados

```markdown
[![CI Pipeline](https://github.com/laddertech/pypix-api/workflows/CI%20Pipeline/badge.svg)](https://github.com/laddertech/pypix-api/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/laddertech/pypix-api/branch/main/graph/badge.svg)](https://codecov.io/gh/laddertech/pypix-api)
[![PyPI version](https://badge.fury.io/py/pypix-api.svg)](https://badge.fury.io/py/pypix-api)
[![Python versions](https://img.shields.io/pypi/pyversions/pypix-api.svg)](https://pypi.org/project/pypix-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checking: MyPy](https://img.shields.io/badge/type%20checking-mypy-blue)](https://mypy-lang.org/)
```

## Configuração de Secrets

### Necessários para CD
```bash
# PyPI deployment
PYPI_TOKEN=pypi-xxx...
TEST_PYPI_TOKEN=pypi-xxx...

# Coverage reporting (opcional)
CODECOV_TOKEN=xxx...
```

### Configurar Secrets
1. Vá para Settings → Secrets and variables → Actions
2. Adicione os tokens necessários
3. Para PyPI, use tokens de API, não senha

## Fluxo de Desenvolvimento

### Para Pull Requests
```mermaid
graph LR
    A[PR criado] --> B[CI: Quality]
    B --> C[CI: Test Matrix]
    C --> D[CI: Build]
    D --> E[✅ CI Success]
```

### Para Releases
```mermaid
graph LR
    A[Create Release] --> B[CD: Pre-deploy]
    B --> C[CD: Deploy to PyPI]
    C --> D[CD: Verification]
    D --> E[CD: Update Notes]
    E --> F[✅ Deploy Success]
```

## Comandos Locais

### Simular CI localmente
```bash
# Verificações de qualidade
make quality

# Testes com cobertura
make test-cov

# Build completo
make build
```

### Testar diferentes versões Python
```bash
# Instalar pyenv para gerenciar versões
pyenv install 3.11
pyenv install 3.12

# Testar em cada versão
pyenv local 3.11
make test

pyenv local 3.12
make test
```

## Monitoramento

### Status Checks
- **Required status checks**: quality, test, build
- **Branch protection**: Configurar no GitHub
- **Auto-merge**: Quando todos os checks passam

### Relatórios
- **Coverage**: Codecov dashboard
- **Build artifacts**: GitHub Actions artifacts
- **Test results**: GitHub Actions summary

## Troubleshooting

### CI falhando

#### Quality checks fail
```bash
# Localmente
make quality

# Corrigir automaticamente
make fix
```

#### Tests fail em versão específica
```bash
# Testar localmente com pyenv
pyenv local 3.12
make test
```

#### Build fails
```bash
# Verificar build localmente
make build
twine check dist/*
```

### CD falhando

#### Deploy to PyPI fails
1. Verificar se token está válido
2. Verificar se versão não existe já
3. Verificar se package build é válido

#### Verification fails
1. PyPI pode demorar para indexar
2. Aguardar alguns minutos e tentar novamente

## Melhorias Futuras

### Performance
- [ ] Cache mais agressivo
- [ ] Paralelização de jobs
- [ ] Conditional execution

### Quality
- [ ] Code scanning com CodeQL
- [ ] Dependency review
- [ ] SAST tools adicionais

### Monitoring
- [ ] Slack/Discord notifications
- [ ] Performance regression detection
- [ ] Deploy metrics

### Automation
- [ ] Auto-merge para PRs de dependências
- [ ] Automatic version bumping
- [ ] Automated security updates

## Boas Práticas

### Branch Strategy
```bash
main        # Produção (releases)
develop     # Desenvolvimento (features)
feature/*   # Features específicas
hotfix/*    # Correções urgentes
```

### Commit Messages
```bash
feat: adiciona nova funcionalidade
fix: corrige bug crítico
docs: atualiza documentação
ci: melhora pipeline
```

### Release Process
1. **Feature complete** em `develop`
2. **Create release branch** (`release/v1.2.0`)
3. **Final testing** e bug fixes
4. **Merge to main** e tag
5. **GitHub release** (triggers CD)

## Security

### Secrets Management
- Use GitHub secrets, nunca hardcode
- Rotate tokens regularmente
- Use trusted publishing quando possível

### Permissions
```yaml
permissions:
  contents: read        # Ler código
  id-token: write      # Trusted publishing
  actions: read        # Ler outros workflows
```

### Supply Chain
- Pin action versions (`@v4`, não `@main`)
- Review dependencies regularmente
- Use dependabot para updates

## Recursos Adicionais

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [Codecov Documentation](https://docs.codecov.com/)
- [uv Documentation](https://docs.astral.sh/uv/)
