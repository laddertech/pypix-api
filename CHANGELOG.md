# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ✨ Parâmetro `timeout` em `BankPixAPIBase` e `OAuth2Client`, no formato nativo do `requests`
  (um número ou a tupla `(conexão, leitura)`). Padrão: `(5.0, 30.0)`, exposto em
  `pypix_api.http.DEFAULT_TIMEOUT`
- ✨ `PixErroTransporteException` e suas filhas `PixTimeoutException` e `PixConexaoException`,
  para falhas ocorridas antes de haver resposta HTTP. Herdam de `PixAPIException`, então um único
  `except` cobre erros do PSP e falhas de transporte. Nelas, `status` é `None`
- ✨ `BankPixAPIBase._request()`: ponto único de saída HTTP da biblioteca. Garante o timeout,
  monta os headers de autenticação e trata a resposta de erro. Aceita `extra_headers` para
  headers adicionais — os de autenticação não são sobrescrevíveis
- ✨ `PixNaoAutorizadoException` (401) e `PixErroServidorException` (500). Com elas, **todo** erro
  HTTP passa a virar uma exceção da hierarquia `PixAPIException` — antes, status fora de
  `{400, 403, 404, 503}` vazavam `requests.HTTPError`
- ✨ O campo `violacoes` do corpo de erro — onde o PSP explica a recusa de um 400 — passa a ser
  preenchido nas exceções e a aparecer na mensagem
- ✨ A hierarquia de exceções mudou de `pypix_api.banks.exceptions` para `pypix_api.exceptions`,
  porque o `auth` também a usa. O módulo antigo reexporta tudo — os imports existentes continuam
  válidos
- ✅ Testes do tratamento de erro, do timeout e das respostas sem corpo
  (`tests/tests_mock/test_request_base.py`), além dos helpers `make_response` e
  `assert_requisicao` no `conftest`
- 📝 Seções "Timeout" e "Idempotência: o que fazer depois de um timeout" no README, com a tabela
  de quais operações podem ser repetidas com segurança

### Changed
- ⚠️ **Toda requisição passa a ter tempo limite.** Antes, sem `timeout`, o `requests` esperava
  indefinidamente — uma resposta que nunca chegava prendia o processo sem log nem métrica. Quem
  dependia desse comportamento deve passar `timeout=(5.0, None)`; `timeout=None` significa
  "use o padrão"
- ♻️ Os 50 pontos de chamada HTTP dos mixins passam a usar `_request()` no lugar de
  `self.session.<verbo>(...)` seguido de `_handle_error_response`

### Fixed
- 🐛 `excluir_webhook`, `excluir_webhook_cobr` e `excluir_webhook_rec` levantavam
  `PixRespostaInvalidaError` diante de uma resposta **204**: o tratamento de erro exigia
  `Content-Type: application/json`, que um 204 sem corpo não traz. Respostas sem corpo passam a
  ser aceitas
- 🐛 `_handle_error_response` desviava do mapeamento de exceções quando a resposta era um `Mock`
  (`hasattr(response, '_mock_return_value')`) — código de teste no caminho de produção. Como
  efeito colateral, **nenhum teste exercitava o tratamento de erro real**: os testes de erro
  substituíam o método por um fake. O desvio foi removido e os testes reescritos com
  `requests.Response` de verdade
- 🐛 A requisição de token não tinha timeout e podia prender um worker indefinidamente
- 🐛 Erros com corpo vazio (um 500 sem corpo, por exemplo) escapavam do tratamento: `excluir_webhook`
  devolvia `False` — uma falha lida como "não excluiu" — e as demais chamadas vazavam
  `JSONDecodeError`. Respostas sem corpo passam a ser aceitas apenas quando o status é de sucesso
- 🐛 Erros cujo corpo não é JSON (HTML de proxy, texto puro) viravam `PixRespostaInvalidaError`,
  descartando a informação do status. Agora viram a exceção do status, com o corpo em `detail`
- 🐛 Corpo de erro em JSON válido mas fora do formato de objeto (`null`, lista, número) vazava
  `AttributeError`, porque `null` não levanta `ValueError` no `json()`. O mesmo valia para campos
  nulos (`"type": null`), que vazavam `TypeError`
- 🐛 O `status` do corpo é coagido para inteiro: PSPs que o enviam como string (`"status": "404"`)
  caíam silenciosamente em `PixErroDesconhecidoException`
- 🐛 Respostas 2xx sem corpo fora de 204/205 passavam pelo tratamento e vazavam `JSONDecodeError`
  no `resp.json()` do método chamador. Agora levantam `PixRespostaInvalidaError`
- 🐛 Itens de `violacoes` fora do formato de objeto (`[null]`, `["texto"]`, listas mistas) faziam a
  **construção da exceção** estourar com `AttributeError`, destruindo o status e o detalhe do erro
  que ela deveria descrever. Itens inválidos passam a ser descartados
- 🐛 Erros HTTP do endpoint de token vazavam `requests.HTTPError`, fora da hierarquia da biblioteca —
  justamente no caminho percorrido antes de toda operação autenticada. Passam a virar a exceção do
  status, com `error`/`error_description` da RFC 6749 preservados em `detail`
- 🐛 Uma resposta de token sem `access_token`/`expires_in` (200 vazio, `null`, objeto incompleto)
  estourava `JSONDecodeError` ou `KeyError` no meio da chamada de negócio. Agora levanta
  `PixRespostaInvalidaError`. `expires_in` como string é convertido em vez de estourar `TypeError`
- 🐛 **Corpos de erro em `application/problem+json` eram descartados.** A especificação do BACEN
  declara todo corpo de erro nesse content-type, e a checagem exigia `application/json` — com um PSP
  conforme, `type`, `status` e `violacoes` se perdiam. Qualquer subtipo JSON passa a ser reconhecido
- 🐛 `criar_lote_cobv`, `alterar_lote_cobv` e os três `configurar_webhook*` levantavam
  `PixRespostaInvalidaError` em chamadas **bem-sucedidas**: a especificação define 202 (lote) e 200
  (webhook) sem corpo. A decisão de exigir corpo passou do tratamento de erro para cada método
- 🐛 Erros com corpo JSON fora do padrão do BACEN (formato próprio de gateway) produziam exceção com
  `detail` vazio — a recusa chegava ao consumidor sem motivo algum
- 🐛 Acentuação do corpo cru era corrompida quando o PSP não declarava `charset` no `Content-Type`
  ("inválida" virava "inv√°lida" no log). JSON é UTF-8 por definição (RFC 8259)
- 🐛 `extra_headers` em conflito levantava `ValueError` só depois de solicitar um token ao PSP

## [0.10.0] - 2026-07-25

### Added
- ✨ Novo módulo `pypix_api.models.enums` com os status da especificação do BACEN:
  `StatusCob`, `StatusCobR`, `StatusRec`, `StatusSolicRec` e `PoliticaRetentativa`.
  Herdam de `str`, então comparam direto com as respostas cruas da API e
  serializam corretamente em JSON. Exportados no pacote raiz
- ✨ `gerar_id_rec(ispb, politica_retentativa, data_criacao, sequencial)` em
  `pypix_api.utils.identificadores`, que monta o `idRec` conforme a regra de
  formação do schema `RecId` (`RAxxxxxxxxyyyyMMddkkkkkkkkkkk`). O segundo
  caractere é derivado da política de retentativa, impedindo a contradição entre
  o identificador e o campo `politicaRetentativa` — inconsistência que o schema
  não detecta, já que o `pattern` só valida 29 caracteres alfanuméricos
- ✨ Helpers de cancelamento que dispensam montar o corpo à mão:
  `cancelar_cobr(txid)`, `cancelar_recorrencia(id_rec)` e
  `cancelar_solicrec(id_solic_rec)`. Todos delegam ao respectivo `revisar_*` com
  `{"status": "CANCELADA"}` — `cancelar_cobr` encerra apenas a cobrança do ciclo,
  mantendo a recorrência ativa

### Fixed
- 🐛 Corrige o exemplo da docstring de `revisar_solicrec`, que indicava
  `{"status": "REJEITADA", "motivo": ...}` — o schema `SolicRecRevisada` aceita
  apenas `status: CANCELADA`, e `REJEITADA` é um status de resposta do PSP do
  pagador. O teste que replicava o exemplo incorreto também foi corrigido

### Documentation
- 📝 Novo guia `docs/examples/pix_automatico.rst` com o fluxo de Pix Automático
  (`rec` → `solicrec` → `cobr`), a tabela de status escrivíveis por recurso, a
  regra de formação do `idRec` e a distinção entre cancelar uma CobR e cancelar
  a recorrência inteira
- 📝 Documenta nos `revisar_*` e nos `cancelar_*` o único status aceito e a
  precondição que faz o PSP recusar o cancelamento com 400: para a CobR, data
  igual ou posterior à primeira tentativa de liquidação; para a Rec, já estar
  expirada, cancelada ou rejeitada; para a SolicRec, status diferente de
  `CRIADA`, `ENVIADA` ou `RECEBIDA`
- 📝 Aviso em `docs/examples/recurring.rst`, que apesar do nome trata de `cobv`

## [0.9.2] - 2026-07-24

### Documentation
- 📝 Adiciona exemplo de uso completo do **Sicredi** (bloco no README + guia
  `docs/examples/sicredi_basic.rst`), destacando o `client_secret` (HTTP Basic)
- 📝 Inclui o Sicredi no sumário e na referência de bancos do README
- 🖼️ Corrige a logo do README para URL absoluta, permitindo a renderização na
  página do PyPI (caminho relativo não é resolvido pelo PyPI)

### Note
- Release **somente de documentação**: nenhuma mudança de API ou de comportamento
  em relação à `0.9.1`.

## [0.9.1] - 2026-07-24

### Documentation
- 📝 Alinha toda a documentação à realidade do código (v0.9.x): corrige exemplos
  quebrados no README e nos guias (`BBPixAPI`/`SicoobPixAPI`/`SicrediPixAPI`,
  `token_url` obrigatório, remoção de parâmetros inexistentes
  `cert_path`/`cert_password`/`scope`) e chamadas inválidas (`configurar_webhook`,
  `listar_cobv`)
- 📝 Documenta o Sicredi, os mixins de métodos faltantes e os módulos de
  observabilidade; esclarece que a observabilidade é opt-in e não instrumenta
  automaticamente as chamadas HTTP
- 📝 Atualiza a versão da documentação Sphinx (`conf.py`), as versões suportadas em
  `SECURITY.md` e o roadmap do CHANGELOG
- 🧹 Corrige formatação RST em docstrings de mixins (sem mudança de comportamento)

### Note
- Release **somente de documentação**: nenhuma mudança de API ou de comportamento
  em relação à `0.9.0`.

## [0.9.0] - 2026-07-22

### Added
- 🏦 **Integração com o Sicredi** (código 748) reaproveitando a estrutura BACEN:
  cobrança imediata em v3 (por txid) / v2 (coleção), Pix comum em v2 e Pix
  Automático em v1, sobre a raiz `/api`
- Autenticação HTTP Basic opcional (`client_secret`) no `OAuth2Client`, exigida
  pelo Sicredi
- Helper `_endpoint_url` na base para versionamento de API por recurso
  (retrocompatível; sem impacto em BB/Sicoob)

### Fixed
- Benchmarks de OAuth2 (`tests/benchmarks/test_oauth_performance.py`) alinhados à
  assinatura real do `OAuth2Client`
- Sincronização de `__version__` em `pypix_api/__init__.py` com o `pyproject.toml`

## [0.6.2] - 2025-01-09

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

Já entregue desde o roadmap original:
- [x] Cache de tokens por escopo (`OAuth2Client`)
- [x] Retry com backoff e observabilidade opt-in (`error_handling`, `logging`, `metrics`)
- [x] Operações em lote de CobV (`LoteCobVMethods`)
- [x] Novos bancos: Sicredi (código 748), além de BB e Sicoob

#### Próximas versões
- [ ] Suporte para mais bancos (ex.: Caixa, Itaú)
- [ ] Async/await support
- [ ] Webhook server helpers
- [ ] Observabilidade plugada automaticamente no caminho HTTP dos mixins

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
