<div align="center">
  <img src="https://raw.githubusercontent.com/laddertech/pypix-api/main/docs/_static/images/logo.png" alt="PyPix-API" width="400"/>

  # pypix-api
</div>

[![CI Pipeline](https://github.com/laddertech/pypix-api/workflows/CI%20Pipeline/badge.svg)](https://github.com/laddertech/pypix-api/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/laddertech/pypix-api/branch/main/graph/badge.svg)](https://codecov.io/gh/laddertech/pypix-api)
[![PyPI version](https://badge.fury.io/py/pypix-api.svg)](https://badge.fury.io/py/pypix-api)
[![Python versions](https://img.shields.io/pypi/pyversions/pypix-api.svg)](https://pypi.org/project/pypix-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checking: MyPy](https://img.shields.io/badge/type%20checking-mypy-blue)](https://mypy-lang.org/)

Biblioteca em Python para comunicação com APIs bancárias, focada na integração com o PIX.

## Sumário

- [pypix-api](#pypix-api)
  - [Sumário](#sumário)
  - [Visão Geral](#visão-geral)
  - [Instalação](#instalação)
  - [Documentação](#documentação)
  - [Exemplo de Uso](#exemplo-de-uso)
    - [Banco do Brasil](#banco-do-brasil)
    - [Sicoob](#sicoob)
    - [Sicredi](#sicredi)
  - [Estrutura do Projeto](#estrutura-do-projeto)
  - [Configuração](#configuração)
    - [Parâmetros de Inicialização](#parâmetros-de-inicialização)
    - [URLs das APIs](#urls-das-apis)
  - [Testes](#testes)
  - [Contribuição](#contribuição)
  - [Segurança](#segurança)
  - [Licença](#licença)

## Visão Geral

O `pypix-api` facilita a integração de sistemas Python com APIs bancárias brasileiras, com ênfase no ecossistema do PIX. A biblioteca abstrai autenticação, comunicação segura (mTLS/OAuth2), e operações comuns de bancos como **Banco do Brasil** (001), **Sicoob** (756) e **Sicredi** (748).

Além das cobranças (imediata, com vencimento e em lote), cobre Pix Automático (recorrências), locations, consultas de Pix/devoluções e webhooks. Inclui ainda um módulo opcional de observabilidade (logging estruturado, métricas e tratamento de erros).

## Instalação

```bash
pip install pypix-api
```

Ou, para desenvolvimento:

```bash
git clone https://github.com/laddertech/pypix-api.git
cd pypix-api
pip install -e ".[dev]"
```

## Documentação

📚 **Documentação Completa**: [Sphinx Docs](docs/_build/html/index.html) (local) | [GitHub Pages](https://laddertech.github.io/pypix-api/)

### Guias Específicos

- 📋 **[Guia de Contribuição](CONTRIBUTING.md)** - Como contribuir para o projeto
- 🔒 **[Política de Segurança](SECURITY.md)** - Relatório de vulnerabilidades e boas práticas
- 📝 **[Histórico de Mudanças](CHANGELOG.md)** - Todas as versões e alterações
- 🔧 **Guias de Desenvolvimento**:
  - [CI/CD Pipeline](docs/CI_CD_GUIDE.md) - Configuração do pipeline
  - [Pre-commit Hooks](docs/PRE_COMMIT_GUIDE.md) - Hooks de qualidade
  - [Cobertura de Testes](docs/TESTING_COVERAGE_GUIDE.md) - Estratégia de testes
  - [Type Checking](docs/TYPE_CHECKING_GUIDE.md) - Verificação de tipos

### Referência da API

- 🏦 **[Bancos](docs/api/banks.rst)** - Banco do Brasil, Sicoob, Sicredi
- 🔐 **[Autenticação](docs/api/auth.rst)** - OAuth2, mTLS
- 📊 **[Modelos](docs/api/models.rst)** - Estruturas de dados PIX
- 🎯 **[Scopes](docs/api/scopes.rst)** - Gerenciamento de escopos OAuth2

### Exemplos

- 🏦 **[Banco do Brasil - Básico](docs/examples/bb_basic.rst)**
- 🏛️ **[Sicoob - Básico](docs/examples/sicoob_basic.rst)**
- 🌱 **[Sicredi - Básico](docs/examples/sicredi_basic.rst)**
- 🪝 **[Configuração de Webhooks](docs/examples/webhooks.rst)**
- 🔄 **[Pagamentos Recorrentes](docs/examples/recurring.rst)**

Para gerar a documentação localmente:

```bash
make docs
make docs-serve  # Servidor local na porta 8000
```

## Exemplo de Uso

### Banco do Brasil

```python
from pypix_api.banks.bb import BBPixAPI

from pypix_api.auth.oauth2 import OAuth2Client

# Primeiro crie o cliente OAuth2 (o token_url vem da classe do banco)
oauth = OAuth2Client(
    token_url=BBPixAPI.TOKEN_URL,
    client_id="SEU_CLIENT_ID",
    cert="caminho/do/certificado.pem",  # ou use cert_pfx/pwd_pfx para .pfx
    pvk="caminho/da/chave.key",
)

# Depois instancie o banco passando o OAuth2Client
bb = BBPixAPI(oauth=oauth)

# Exemplo: Cobrança com Vencimento
payload = {
    "calendario": {
        "dataDeVencimento": "2025-12-31",
        "validadeAposVencimento": 30
    },
    "loc": {
        "id": 789
    },
    "devedor": {
        "logradouro": "Alameda Souza, Numero 80, Bairro Braz",
        "cidade": "Recife",
        "uf": "PE",
        "cep": "70011750",
        "cpf": "12345678909",
        "nome": "Francisco da Silva"
    },
    "valor": {
        "original": "123.45",
        "multa": {
            "modalidade": "2",
            "valorPerc": "15.00"
        },
        "juros": {
            "modalidade": "2",
            "valorPerc": "2.00"
        },
        "desconto": {
            "modalidade": "1",
            "descontoDataFixa": [
                {
                    "data": "2025-11-30",
                    "valorPerc": "30.00"
                }
            ]
        }
    },
    "chave": "5f84a4c5-c5cb-4599-9f13-7eb4d419dacc",
    "solicitacaoPagador": "Cobrança dos serviços prestados."
}

# Criar cobrança com vencimento
cobv = bb.criar_cobv(txid="uuid-unico", body=payload)
print(cobv)
```

### Sicoob

```python
from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.sicoob import SicoobPixAPI

# Cada banco tem seu próprio token_url, então crie um OAuth2Client para o Sicoob
oauth_sicoob = OAuth2Client(
    token_url=SicoobPixAPI.TOKEN_URL,
    client_id="SEU_CLIENT_ID",
    cert_pfx="caminho/do/certificado.pfx",
    pwd_pfx="senha-do-pfx",
)

# Instanciação do Sicoob
sicoob = SicoobPixAPI(oauth=oauth_sicoob)

# Exemplo: Cobrança imediata
payload_cob = {
    "calendario": {
        "expiracao": 3600
    },
    "devedor": {
        "cpf": "12345678909",
        "nome": "Francisco da Silva"
    },
    "valor": {
        "original": "37.00"
    },
    "chave": "5f84a4c5-c5cb-4599-9f13-7eb4d419dacc",
    "solicitacaoPagador": "Pagamento de serviços."
}

cob = sicoob.criar_cob(txid="uuid-unico-2", body=payload_cob)
print(cob)
```

### Sicredi

O Sicredi exige autenticação **HTTP Basic**, então o `OAuth2Client` recebe também o
`client_secret` (além do certificado). O banco usa versionamento por recurso, resolvido
internamente pela própria `SicrediPixAPI`.

```python
from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.sicredi import SicrediPixAPI

# Sicredi: client_secret é obrigatório (Authorization: Basic)
oauth_sicredi = OAuth2Client(
    token_url=SicrediPixAPI.TOKEN_URL,
    client_id="SEU_CLIENT_ID",
    client_secret="SEU_CLIENT_SECRET",
    cert_pfx="caminho/do/certificado.pfx",
    pwd_pfx="senha-do-pfx",
)

# Instanciação do Sicredi
sicredi = SicrediPixAPI(oauth=oauth_sicredi)

# Exemplo: Cobrança imediata
payload_cob = {
    "calendario": {
        "expiracao": 3600
    },
    "devedor": {
        "cpf": "12345678909",
        "nome": "Francisco da Silva"
    },
    "valor": {
        "original": "37.00"
    },
    "chave": "5f84a4c5-c5cb-4599-9f13-7eb4d419dacc",
    "solicitacaoPagador": "Pagamento de serviços."
}

cob = sicredi.criar_cob(txid="uuid-unico-3", body=payload_cob)
print(cob)
```

## Estrutura do Projeto

```
pypix_api/
├── auth/               # Autenticação (mTLS, OAuth2)
├── banks/              # Integrações com bancos (BB, Sicoob, Sicredi)
│   └── methods/        # Mixins de operações PIX (cob, cobv, cobr, lote, loc, pix, rec, webhooks)
├── models/             # Modelos de dados do PIX (PixCobranca)
├── scopes/             # Registro e definição de escopos OAuth2 por banco
├── error_handling.py   # Framework de erros (opcional / observabilidade)
├── logging.py          # Logging estruturado (opcional)
├── metrics.py          # Coleta de métricas (opcional)
└── observability.py    # Orquestração de observabilidade (opcional)
tests/                  # Testes automatizados (tests_mock, tests_integration, benchmarks)
openapi.yaml            # Especificação OpenAPI de referência
pyproject.toml          # Configuração do projeto Python
Makefile                # Comandos úteis para desenvolvimento
.env.exemplo            # Exemplo de variáveis de ambiente
```

## Configuração

### Parâmetros de Inicialização

1. Primeiro crie uma instância de OAuth2Client:
```python
from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.bb import BBPixAPI

oauth = OAuth2Client(
    token_url=BBPixAPI.TOKEN_URL,       # URL de token do banco (obrigatório)
    client_id="SEU_CLIENT_ID",          # ID do cliente fornecido pelo banco
    cert="caminho/do/certificado.pem",  # Certificado digital PEM (.pem)
    pvk="caminho/da/chave.key",         # Chave privada PEM (.key)
    # Alternativa a cert/pvk: cert_pfx="cert.pfx", pwd_pfx="senha"
    # client_secret="...",  # obrigatório para o Sicredi (HTTP Basic)
)
```

2. Depois instancie o banco passando o OAuth2Client:
```python
banco = BBPixAPI(oauth=oauth)  # Ou SicoobPixAPI(oauth=oauth) / SicrediPixAPI(oauth=oauth)
```

### Escopos OAuth2

Os escopos Pix são liberados **por credencial**, conforme as modalidades que o associado
contratou com o PSP. Por padrão a biblioteca pede o grupo Pix **completo** do banco — no
Sicredi, 22 escopos. Se a credencial só tem parte das modalidades, isso pede permissão a mais
e, dependendo do PSP, resulta em `400 — Escopo Negado` ou na concessão silenciosa de apenas
o subconjunto liberado.

Informe em `scopes=` exatamente o que a credencial tem. O helper `compose_scopes` monta a
string a partir dos nomes dos grupos:

```python
from pypix_api.banks.sicredi import SicrediPixAPI
from pypix_api.scopes import compose_scopes

# Pix Automático: cobrança imediata + recorrência, sem cobv/lotecobv/location
scopes = compose_scopes(
    "748", "cob", "cobr", "rec", "solicrec", "webhook_rec", "webhook_cobr"
)
sicredi = SicrediPixAPI(oauth=oauth_sicredi, scopes=scopes)
```

O parâmetro aceita também um `ScopeGroup`, uma lista de escopos e uma lista de grupos:

```python
from pypix_api.scopes.sicredi import SicrediScopes

banco = SicrediPixAPI(oauth=oauth_sicredi, scopes=SicrediScopes.COBR)
banco = SicrediPixAPI(oauth=oauth_sicredi, scopes=["cob.read", "cob.write"])
banco = SicrediPixAPI(oauth=oauth_sicredi, scopes=[SicrediScopes.COB, SicrediScopes.COBR])
```

Omitir o parâmetro (ou passar `None`) mantém o grupo completo do banco. Um valor **vazio**
(`""` ou `[]`) levanta `ValueError` — um conjunto vazio não vira silenciosamente "todos os
escopos".

Os grupos disponíveis de cada banco podem ser listados em runtime:

```python
from pypix_api.scopes import ScopeRegistry

ScopeRegistry.list_scope_groups("748")
# ['COB', 'COBR', 'COBV', 'LOCATION', 'LOTECOBV', 'PIX', 'PIX_BASIC',
#  'REC', 'SOLICREC', 'WEBHOOK', 'WEBHOOK_COBR', 'WEBHOOK_REC']
```

Quando o PSP devolve o token concedendo **menos** escopos do que os solicitados, a biblioteca
registra um `WARNING` no logger `pypix_api.auth.oauth2` com os que faltaram — sem isso, a
modalidade não contratada só apareceria como erro no endpoint de negócio, longe da causa.

### Timeout

Toda requisição da biblioteca — incluindo a de token — leva timeout. O padrão é
`(5s para conectar, 30s para ler)`.

**O banco e o `OAuth2Client` têm timeouts independentes** — só o valor padrão é comum. Para
ajustar as duas pontas, informe em cada uma:

```python
oauth = OAuth2Client(token_url=..., client_id=..., timeout=(5.0, 15.0))  # requisição de token
banco = BBPixAPI(oauth=oauth, timeout=(5.0, 60.0))                       # chamadas de negócio
banco = BBPixAPI(oauth=oauth, timeout=(5.0, None))                       # leitura sem limite
```

`timeout=None` significa "use o padrão", não "espere para sempre". Para leitura sem limite,
use `(conexão, None)`, no formato nativo do `requests`.

Um estouro de tempo levanta `PixTimeoutException`; uma falha de rede, `PixConexaoException`.
Ambas herdam de `PixErroTransporteException` — que por sua vez herda de `PixAPIException`,
então um único `except` cobre erros do PSP e falhas de transporte. Como não houve resposta
HTTP, o atributo `status` dessas exceções é `None`.

### Erros devolvidos pelo PSP

Toda resposta de erro vira uma exceção tipada, inclusive quando o corpo vem vazio ou fora do
padrão do BACEN — nesse caso o texto da resposta é preservado em `detail`, que é o que os PSPs
pedem para abrir chamado:

| Status | Exceção |
|---|---|
| 400 | `PixErroValidacaoException` |
| 401 | `PixNaoAutorizadoException` |
| 403 | `PixAcessoNegadoException` |
| 404 | `PixRecursoNaoEncontradoException` |
| 500 | `PixErroServidorException` |
| 503 | `PixErroServicoIndisponivelException` |
| outros | `PixErroDesconhecidoException` |

O campo `violacoes` do corpo — onde o PSP explica a recusa de um 400 (chave Pix não encontrada,
escopo negado, thumbprint incorreto) — fica disponível em `exc.violacoes` e entra na mensagem
da exceção:

```python
try:
    banco.criar_cob(txid, body)
except PixErroValidacaoException as exc:
    logger.warning('Cobrança recusada: %s', exc)   # inclui as violações
    for violacao in exc.violacoes:
        tratar(violacao['propriedade'], violacao['razao'])
```

### Idempotência: o que fazer depois de um timeout

Um `PixTimeoutException` significa **estado desconhecido**, não "não criou": o PSP pode ter
processado a requisição e apenas a resposta ter se perdido.

| Operações | Depois de um timeout |
|---|---|
| `PUT /cob/{txid}`, `/cobv/{txid}`, `/cobr/{txid}`, `/lotecobv/{id}`, `/pix/{e2eid}/devolucao/{id}`, `/webhook/{chave}`, `/webhookrec`, `/webhookcobr` | Pode repetir — o identificador é seu |
| `PATCH /cob/{txid}`, `/cobv/{txid}`, `/cobr/{txid}`, `/rec/{idRec}`, `/solicrec/{id}`, `/lotecobv/{id}` | Pode repetir; o contador de revisão sobe a cada chamada. Para cancelamento é seguro |
| `POST /cob`, `/cobr`, `/rec`, `/solicrec`, `/loc`, `/locrec` | **Consulte antes de recriar** — o identificador é gerado pelo PSP |
| `POST /cobr/{txid}/retentativa/{data}` | Consulte antes de repetir — comportamento não documentado pelo PSP |

A biblioteca **não faz retry automático**. Repetição é decisão do consumidor, que é quem sabe
se a operação é segura de repetir.

### URLs das APIs

As URLs base e de token são definidas por cada classe de banco (`BASE_URL`/`TOKEN_URL`):

- **Banco do Brasil**: classe `BBPixAPI`
- **Sicoob**: classe `SicoobPixAPI`
- **Sicredi**: classe `SicrediPixAPI` — usa versionamento por recurso (raiz `/api`) e exige `client_secret` (HTTP Basic) no `OAuth2Client`

Crie um arquivo `.env` baseado em `.env.exemplo` com as credenciais e configurações necessárias para autenticação e acesso às APIs bancárias.

## Testes

Para rodar os testes automatizados:

```bash
make test
```
ou diretamente com pytest:
```bash
pytest
```

## Contribuição

Contribuições são bem-vindas! Por favor, consulte nosso **[Guia de Contribuição](CONTRIBUTING.md)** para informações detalhadas sobre:

- Como configurar o ambiente de desenvolvimento
- Padrões de código e commits
- Processo de Pull Request
- Executar testes e verificações de qualidade

Para entender nossos templates e automações GitHub, veja **[.github/GITHUB_TEMPLATES.md](.github/GITHUB_TEMPLATES.md)**.

Passos rápidos:

1. Fork este repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas alterações (`git commit -am 'feat: adiciona nova funcionalidade'`)
4. Execute os testes (`make quality-full`)
5. Push para a branch (`git push origin feature/nova-funcionalidade`)
6. Abra um Pull Request

## Segurança

Para reportar vulnerabilidades de segurança, consulte nossa **[Política de Segurança](SECURITY.md)**.

**NÃO** reporte vulnerabilidades através de issues públicos.

## Licença

Este projeto está licenciado sob os termos da licença MIT.
