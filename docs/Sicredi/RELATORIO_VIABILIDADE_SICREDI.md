# Relatório de Viabilidade — Integração do Sicredi (PIX) no pypix-api

> **Objetivo:** avaliar se é possível adicionar o **Sicredi** à biblioteca `pypix-api`
> (hoje com suporte a Banco do Brasil e Sicoob) **sem comprometer os bancos existentes**,
> com escopo **completo** (Pix comum v2/v3 + Pix Automático v1).
>
> **Fontes:** código atual do repositório + documentação em `docs/Sicredi/`
> (`CollectionAPIPixSicredi.json` e `Guia_tecnico_integracoes_APIPix_Sicredi_v1.9.5.pdf`).

---

## 1. Veredito

✅ **É possível integrar o Sicredi sem comprometer BB e Sicoob** — porém **não** é um
simples "copiar o Sicoob".

A arquitetura atual é sólida e cerca de **85% compatível** com o Sicredi, já que o banco
segue o padrão BACEN nos endpoints. No entanto, o Sicredi tem **2 desvios estruturais** em
relação ao que a camada base assume hoje. Ambos são resolvíveis com **extensões aditivas e
retrocompatíveis (opt-in)** na camada compartilhada — o comportamento de BB/Sicoob
permanece **idêntico** (os bytes das requisições não mudam), pois os novos caminhos só são
ativados quando o próprio banco os solicita.

---

## 2. Como a arquitetura atual funciona (base da avaliação)

O projeto separa responsabilidades em **3 camadas** + a camada de autenticação:

- **Camada banco** (`pypix_api/banks/<banco>.py`): define apenas `BASE_URL`,
  `SANDBOX_BASE_URL`, `TOKEN_URL`, `get_bank_code()` e `get_base_url()`. O `SicoobPixAPI`
  tem 38 linhas — é o template natural a copiar.
- **Camada base + mixins** (`banks/base.py` + `banks/methods/*.py`): concentra toda a
  lógica HTTP dos endpoints BACEN, compartilhada por todos os bancos. Os mixins montam a
  URL como `url = f'{self.get_base_url()}/cob/{txid}'` (ver `cob_methods.py:56`).
- **Camada scopes** (`scopes/*.py` + registro em `scopes/__init__.py`): resolve os scopes
  por código do banco em runtime. `_create_headers` chama
  `get_pix_scopes(get_bank_code())` (`base.py:98`); um banco não-registrado gera
  `ValueError`.
- **Autenticação** (`auth/oauth2.py` + `auth/mtls.py`): `OAuth2Client` com
  `client_credentials` + **mTLS** (PEM ou PKCS#12). O token é solicitado enviando no corpo
  apenas `grant_type` + `client_id` + `scope` (`oauth2.py:78-84`), **sem `client_secret` e
  sem `Authorization: Basic`**.

---

## 3. O que o Sicredi exige (extraído da documentação)

| Item | Valor |
|---|---|
| Base de produção | `https://api-pix.sicredi.com.br/api/v2` |
| Base de homologação | `https://api-pix-h.sicredi.com.br/api/v2` *(inferido — não literal na doc; credenciais de homologação são solicitadas por e-mail: `integracoes_pix@sicredi.com.br`)* |
| Endpoint de token | `POST https://api-pix.sicredi.com.br/oauth/token` |
| Autenticação do token | OAuth2 `client_credentials` + **`Authorization: Basic base64(client_id:client_secret)`** + **mTLS obrigatório** |
| Código Febraban | **748** |
| Prefixo de path | `/api/` (e **não** `/pix/`) |
| Versão por recurso | `cob` → **v3**; `cobv` / `pix` / `webhook` → **v2**; Pix Automático (`cobr` / `rec` / `locrec` / `solicrec` / `webhookcobr` / `webhookrec`) → **v1** |
| Scopes | `cob.read/write`, `cobv.read/write`, `lotecobv.read/write`, `cobr.read/write`, `webhook.read/write`, `pix.read` (liberados sob demanda por credencial) |

---

## 4. Análise de compatibilidade ponto a ponto

| Aspecto | Base atual | Sicredi | Compatível? | Ação necessária |
|---|---|---|---|---|
| Endpoints BACEN (`/cob`, `/cobv`, `/pix`, `/rec`…) | ✔ implementados nos mixins | ✔ mesmos paths | ✅ | Nenhuma — reuso total dos mixins |
| Injeção de `OAuth2Client` + mTLS | ✔ PEM/PFX | ✔ exige mTLS | ✅ | Nenhuma — mTLS já suportado |
| Tratamento de erro RFC 7807 | ✔ centralizado | ✔ padrão BACEN | ✅ | Nenhuma |
| Registro de scopes por código | ✔ | precisa do `748` | ⚠️ | Criar `scopes/sicredi.py` + registrar |
| **Auth do token** | corpo `client_id` + `scope`, sem secret/Basic | **Basic `base64(id:secret)`** | ❌ **bloqueador** | Estender `OAuth2Client` (opt-in) |
| **URL por recurso** | `get_base_url()` único + path fixo no mixin | **versões mistas** v1/v2/v3 + prefixo `/api/` | ❌ **bloqueador** | Introduzir resolução de URL por recurso (retrocompatível) |
| `sandbox_mode` | token fixo `SANDBOX_TOKEN`, pula mTLS | homologação exige mTLS + OAuth real | ⚠️ | Usar `sandbox_mode=False` apontando p/ base de homologação (ver §7) |
| Header `client_id` nas chamadas | sempre enviado | não exigido | ✅ | Nenhuma — não atrapalha |

---

## 5. Os dois bloqueadores e a solução retrocompatível

### Bloqueador A — Autenticação Basic + `client_secret`

`OAuth2Client.get_token()` não envia `client_secret` nem header `Authorization: Basic`.
O Sicredi exige ambos. **Solução aditiva:**

- Adicionar o parâmetro `client_secret: str | None = None` ao `__init__` (com fallback
  `os.getenv('CLIENT_SECRET')`), análogo aos demais parâmetros.
- Em `get_token()`: **se** `self.client_secret` estiver definido, enviar
  `Authorization: Basic base64(client_id:client_secret)` no header e ajustar o corpo
  conforme a spec; **senão**, manter exatamente o fluxo atual.
- **Retrocompatibilidade:** BB/Sicoob não passam `client_secret` → cai no ramo `else` →
  requisição idêntica à de hoje. O envio via `data=token_data` já usa
  `application/x-www-form-urlencoded`, alinhado ao guia técnico.

### Bloqueador B — Versionamento misto por recurso + prefixo `/api/`

Os mixins fazem `f'{self.get_base_url()}/cob/{txid}'`, assumindo uma URL base única. O
Sicredi precisa de versão diferente por recurso (`cob`=v3, `cobv`/`pix`/`webhook`=v2, Pix
Automático=v1). **Solução retrocompatível:**

- Introduzir na base um helper de montagem, por exemplo
  `def _endpoint_url(self, path: str) -> str:`, cujo **default** retorna
  `f'{self.get_base_url()}{path}'` (comportamento idêntico ao atual).
- Migração **mecânica** dos mixins: trocar `f'{self.get_base_url()}/cob/{txid}'` por
  `self._endpoint_url(f'/cob/{txid}')` (~12 arquivos, sem mudar a semântica).
- No `SicrediPixAPI`, sobrescrever `_endpoint_url` com um `VERSION_MAP`
  (`{'cob': 'v3', 'cobv': 'v2', 'pix': 'v2', 'webhook': 'v2', 'cobr': 'v1', 'rec': 'v1', …}`)
  que extrai o recurso do path e monta `https://api-pix.sicredi.com.br/api/{versão}/{path}`.
- **Retrocompatibilidade:** BB/Sicoob **não** sobrescrevem `_endpoint_url` → usam o default
  → URLs idênticas às de hoje. A troca dentro dos mixins é comportamentalmente neutra.

---

## 6. Impacto nos bancos existentes (garantia de não-regressão)

Nenhuma mudança altera o caminho de execução de BB/Sicoob: as extensões de auth e de URL
são **opt-in por parâmetro/herança**. Garantias:

- A suíte `tests/tests_mock/` (mixins genéricos via `DummyBankPixAPIBase` + `test_bb_*`)
  deve permanecer 100% verde **sem edição**.
- Nenhum arquivo de BB/Sicoob é tocado; nenhum valor default de assinatura muda.
- Não existe registry central de classes de banco — adicionar o Sicredi não mexe em
  nenhuma estrutura de dispatch existente.

---

## 7. Ponto de atenção — "sandbox" vs "homologação" do Sicredi

O `sandbox_mode=True` do framework usa **token fixo** (`SANDBOX_TOKEN`) e **pula o mTLS** —
ou seja, é um mock local. Já a **homologação do Sicredi é um ambiente real** que exige
mTLS + OAuth. Portanto, para testar contra a homologação do Sicredi deve-se usar
`sandbox_mode=False` apontando para a base de homologação com o certificado de homologação.
Recomenda-se documentar isso claramente; opcionalmente, avaliar no futuro
renomear/desacoplar esse conceito (fora do escopo desta análise).

---

## 8. Lacunas da documentação a confirmar com o Sicredi antes de implementar

1. URL **literal** da base de homologação (ela só aparece como host dentro de uma mensagem
   de erro 403 no PDF).
2. Scopes nomeados de `pix.write`, `rec`, `locrec` e `solicrec` — os endpoints existem no
   Postman, mas os scopes correspondentes não estão explícitos no texto extraído do PDF.
3. `Content-Type` correto do `/oauth/token` (a collection Postman diz `application/json`; o
   PDF diz `x-www-form-urlencoded` — recomenda-se seguir o PDF / padrão OAuth2).
4. Schema/payload dos webhooks do Pix Automático (`webhookcobr` / `webhookrec`).

### 8.1. Confirmado no Guia Técnico v1.9.5 — comportamento de escopos (downscoping)

Uma revisão adversarial levantou o risco de que solicitar o conjunto **completo** de
escopos no token (estratégia atual, herdada do Sicoob) pudesse ser rejeitado com
`invalid_scope` quando a credencial não possui todos, quebrando até a cobrança imediata.
**A documentação do Sicredi refuta esse risco:** o banco faz *downscoping* na emissão do
token. No exemplo oficial do Guia, o `curl` solicita
`scope=cob.write+cob.read+cobv.write+cobv.read+webhook.read+webhook.write`, mas a resposta
retorna apenas `"scope": "cob.read cob.write webhook.read webhook.write"` (sem `cobv`, que
a credencial não tinha) — o token é emitido normalmente, apenas sem os escopos não
liberados. O campo `scope` da resposta é descrito como *"Escopos liberados para o acesso"*.

A falha por escopo ocorre **apenas ao usar um recurso** não habilitado, retornando
`Status 400` com `detail` explicativo (ex.: *"Esta credencial não possui os escopos de
cobrança com vencimento (COBV) habilitados"*), já mapeado por `_handle_error_response`
para `PixErroValidacaoException`. **Conclusão:** pedir o escopo completo é seguro; não é
necessário reduzir nem tornar os escopos configuráveis por causa desse risco.

Também confirmado: o `Content-Type` do `/oauth/token` é `application/x-www-form-urlencoded`
(tabela de header do Guia), alinhado à implementação (`data=` no `requests`).

---

## 9. Esforço estimado (para a implementação futura, se aprovada)

| Frente | Arquivos | Esforço |
|---|---|---|
| `OAuth2Client` com Basic auth | `auth/oauth2.py` | Baixo |
| Resolução de URL por recurso | `banks/base.py` + migração dos ~12 mixins | Médio (mecânico) |
| Classe do banco | `banks/sicredi.py` (novo) | Baixo |
| Scopes | `scopes/sicredi.py` (novo) + `scopes/__init__.py` | Baixo |
| Export público | `pypix_api/__init__.py` | Trivial |
| Testes | `tests/tests_mock/test_sicredi_*.py`, integração, fixture `mock_sicredi_responses` | Médio |
| Docs / metadados | `README.md`, `docs/api/banks.rst`, `CHANGELOG.md`, `CONTRIBUTING.md` | Baixo |

---

## 10. Conclusão

A integração do Sicredi é **viável** e de **risco baixo a médio**. O "custo" real não está
em reescrever a base, e sim em **duas extensões retrocompatíveis** da camada compartilhada
(Basic auth no token e resolução de URL por recurso), ambas construídas de forma aditiva e
opt-in, preservando integralmente o comportamento de Banco do Brasil e Sicoob.
