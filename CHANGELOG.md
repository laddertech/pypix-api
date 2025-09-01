# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2025-01-09

### Added
- 🎯 **Sistema de Observabilidade Completo**
  - Logging estruturado com suporte a JSON e sanitização de dados sensíveis
  - Sistema de métricas com counters, gauges e histogramas
  - Coleta automática de métricas de API calls
  - Tratamento avançado de erros com classificação automática
  - Health checks e monitoramento do sistema
  - Context managers para tracking de operações
  - Decoradores para observabilidade transparente
  - ObservabilityMixin para integração fácil

- 📚 **Melhorias na Documentação**
  - Exemplos práticos de uso do BB e Sicoob
  - Guia completo de error handling
  - Documentação de webhooks e recorrência
  - Exemplos de observabilidade e métricas

- 🔧 **Infraestrutura de Desenvolvimento**
  - Complete CI/CD pipeline with GitHub Actions
  - Pre-commit hooks for code quality automation
  - Type checking with MyPy
  - Test coverage with pytest-cov (65.54% coverage)
  - Security scanning with Bandit and Safety
  - Automated dependency updates
  - Tox configuration for multi-version testing

### Changed
- Improved project structure with better organization
- Enhanced testing infrastructure with fixtures
- Updated development workflow with quality gates
- All `__init__.py` files now have proper `__all__` exports
- Modernized Python packaging with pyproject.toml

### Fixed
- Removed duplicate code in cob_methods.py
- Fixed UTF-8 encoding issues in docstrings
- Corrected pre-commit hook configurations

## [0.5.0] - 2024-09-01

### Added
- Método para consultar PIX individual por e2eid
- Método para solicitar devolução de PIX
- Método para consultar devolução de PIX
- Testes automatizados com pytest
- Integração completa com métodos PIX na API base

### Changed
- Melhorias na estrutura de classes e herança
- Atualização da documentação com exemplos práticos
- Refinamento dos métodos de autenticação

### Fixed
- Correções na validação de parâmetros
- Melhorias no tratamento de erros da API

## [0.4.0] - 2024-08-15

### Added
- Suporte completo para API do Sicoob
- Métodos para webhook de recorrência
- Sistema de scopes OAuth2 aprimorado
- Validações de entrada mais robustas

### Changed
- Refatoração da arquitetura de métodos PIX
- Melhorias na documentação do código
- Otimização do sistema de cache de tokens

## [0.3.0] - 2024-08-01

### Added
- Implementação dos métodos de cobrança com vencimento (CobV)
- Sistema de registry para escopos de bancos
- Métodos de webhook para cobranças
- Suporte para múltiplos certificados

### Changed
- Reestruturação do sistema de escopos
- Melhorias na organização do código
- Atualização das dependências

### Fixed
- Correções no tratamento de respostas HTTP
- Fixes na validação de certificados

## [0.2.0] - 2024-07-15

### Added
- Métodos de recorrência (REC)
- Solicitação de retentativa de cobrança
- Sistema de mixins para organização de métodos
- Tratamento de erros específicos por tipo

### Changed
- Reorganização da estrutura de classes base
- Melhorias na documentação
- Padronização dos métodos de API

## [0.1.0] - 2024-07-01

### Added
- Estrutura inicial do projeto
- Suporte básico para Banco do Brasil
- Autenticação OAuth2 com MTLS
- Métodos básicos de cobrança (COB)
- Sistema de exceções personalizado
- Documentação inicial

### Features Implemented
- 🏦 **Bancos suportados**: Banco do Brasil, Sicoob
- 🔐 **Autenticação**: OAuth2 com certificados mTLS
- 💰 **PIX**: Cobranças imediatas e com vencimento
- 🔄 **Recorrência**: Gestão de cobranças recorrentes
- 🪝 **Webhooks**: Configuração e gerenciamento
- 🔍 **Consultas**: PIX, devoluções e relatórios
- ✅ **Testes**: Cobertura de 65%+ com pytest
- 🛠️ **CI/CD**: Pipeline completo com GitHub Actions

---

## Notas de Versão

### Compatibility
- Python 3.10+ (testado em 3.10, 3.11, 3.12)
- Suporte para Windows, macOS e Linux

### Breaking Changes
- v0.5.0: Mudança na assinatura de alguns métodos de consulta
- v0.4.0: Refatoração do sistema de scopes (migração automática)
- v0.3.0: Reestruturação de exceções (backward compatible)

### Migration Guide

#### From 0.4.x to 0.5.0
```python
# Old
api.consultar_pix(inicio, fim, cpf=None, cnpj=None)

# New
api.consultar_pix(inicio, fim, cpf=cpf, cnpj=cnpj)
```

#### From 0.3.x to 0.4.0
```python
# Old
from pypix_api.scopes import BBScopes

# New
from pypix_api.scopes.bb import BBScopes
```

### Planned Features (Roadmap)

#### v0.6.0 (Next Release)
- [ ] Suporte para mais bancos (Caixa, Itaú)
- [ ] Cache inteligente de tokens
- [ ] Retry automático com backoff
- [ ] Métricas de performance

#### v0.7.0
- [ ] Async/await support
- [ ] Webhook server helpers
- [ ] Batch operations
- [ ] Enhanced logging

#### v1.0.0 (Stable)
- [ ] API estável e documentação completa
- [ ] Suporte para todos os bancos principais
- [ ] Performance otimizada
- [ ] Extensibilidade completa

### Contributors

- [@fabio-thomaz](https://github.com/fabio-thomaz) - Main author and maintainer

### Acknowledgments

- Banco Central do Brasil pela especificação PIX
- Comunidade Python brasileira pelo feedback
- Contribuidores do projeto pelas melhorias

---

**Legend:**
- 🆕 **Added** - New features
- 🔄 **Changed** - Changes in existing functionality
- 🗑️ **Deprecated** - Soon-to-be removed features
- 🚫 **Removed** - Now removed features
- 🐛 **Fixed** - Bug fixes
- 🔒 **Security** - Vulnerability fixes
