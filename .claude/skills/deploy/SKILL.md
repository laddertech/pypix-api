---
name: deploy
description: Publica uma nova versão do pypix-api no PyPI. Use quando o usuário pedir para lançar, publicar, deployar ou "subir" uma nova versão da biblioteca. Encapsula o fluxo completo — checagens, bump de versão, correção da sincronia do __version__, atualização do CHANGELOG, commit, tag e o disparo do workflow de release no GitHub Actions.
---

# Deploy do pypix-api (release para PyPI)

## Como o deploy funciona neste projeto

O deploy é **automatizado via GitHub Actions**, disparado pelo **push de uma tag `vX.Y.Z`** —
não por `make publish`:

1. `git push origin main --tags` com uma tag `vX.Y.Z` dispara `.github/workflows/release.yml`.
2. Esse workflow valida o formato da versão, builda, testa em Python 3.10/3.11/3.12, roda
   security scan e cria o **GitHub Release**. Se **não** for prerelease, publica no **PyPI de
   produção** via *trusted publishing* (`pypa/gh-action-pypi-publish`, environment `pypi`, sem
   token no repo); se for prerelease, publica no **Test PyPI**.
3. Tags com sufixo `-rc`/`-alpha`/`-beta` (ex.: `v0.9.0-rc1`, normalizada para `0.9.0rc1` no
   PyPI conforme PEP 440) são **pré-release** → vão só para o **Test PyPI**. O job
   `publish-pypi` (produção) é pulado pelo guard `is_prerelease == false`.
4. **Sobre o `cd.yml`** (comportamento verificado em `v0.9.0-rc1`): ele escuta
   `release: [published]`. Prereleases emitem `prereleased`, então o `cd.yml` **não dispara**
   em prerelease — o fluxo de rc é limpo, sem ruído. Em release de **produção**, o `cd.yml`
   dispara e seu job `deploy` tenta `twine upload` com `secrets.PYPI_TOKEN`, que **não existe**
   no repo (só há `TWINE_USERNAME`/`TWINE_PASSWORD`) → esse job fica **vermelho**, mas é
   **redundante** com o `publish-pypi` do `release.yml` (trusted publishing), que é quem
   realmente publica. O vermelho do `cd.yml` em produção é ruído esperado, não impede o deploy.

> **Não** use `make publish` (twine local) no fluxo normal — ele existe só para publicação
> manual de emergência e exige `TWINE_USERNAME`/`TWINE_PASSWORD`. O caminho padrão é a tag.

> ⚠️ **Publicar no PyPI é irreversível**: uma versão publicada não pode ser sobrescrita nem
> reenviada. **Sempre confirme o número da versão com o usuário antes de criar a tag.**

## Passo a passo

### 1. Pré-condições (não prosseguir se falhar)
- Estar na branch `main`, com working tree **limpo** (`git status`) e já sincronizada com o
  `origin` (`git push origin main` feito).
- Qualidade verde: `make test` e `make lint`. Opcionalmente a suíte completa
  (`uv run pytest tests/`).

### 2. Escolher o tipo de bump (SemVer) — confirmar com o usuário
- **patch** (`0.8.0 → 0.8.1`): apenas correções.
- **minor** (`0.8.0 → 0.9.0`): novas features retrocompatíveis (ex.: novo banco).
- **major** (`0.8.0 → 1.0.0`): mudanças incompatíveis.

### 3. Bump de versão
Rode `make bump-<tipo>` (ex.: `make bump-minor`). O `scripts/release.py`:
- roda testes + lint,
- atualiza `version` em `pyproject.toml`,
- builda o pacote para validar,
- imprime os próximos passos (não faz commit/tag automaticamente).

> ⚠️ **Bug conhecido a verificar** (`__version__`): `scripts/release.py` atualiza
> `pypix_api/__init__.py` fazendo `replace` da versão **atual do pyproject** dentro do
> arquivo. Se `__version__` já estiver dessincronizado do `pyproject.toml`, o `replace`
> **não casa** e o `__init__.py` fica com a versão antiga. (Foi o caso até `0.9.0-rc1`, quando
> a dessincronia `0.6.2` vs `0.8.0` foi corrigida manualmente.) **Sempre confira** após o bump
> que `pyproject.toml` e `pypix_api/__init__.py` têm a **mesma** `X.Y.Z`; se divergirem,
> corrija o `__init__.py` manualmente.

> ⚠️ **`uv.lock` + hook de pré-commit**: mudar a `version` no `pyproject.toml` faz o hook
> `pytest-check` reinstalar o pacote e alterar o `uv.lock` (a versão do próprio pacote no
> lock), o que **aborta o commit** com "files were modified by this hook". Inclua o `uv.lock`
> no commit do bump (ver passo 5). A versão prerelease `X.Y.Z-rcN` é normalizada para
> `X.Y.ZrcN` no build/PyPI (PEP 440) — esperado.

### 4. Atualizar o CHANGELOG
O projeto segue [Keep a Changelog](https://keepachangelog.com/). Mova o conteúdo de
`## [Unreleased]` para uma nova seção `## [X.Y.Z] - AAAA-MM-DD` (data de hoje) e deixe
`[Unreleased]` vazio. Resuma as mudanças reais do release.

### 5. Commit do bump
```bash
git add pyproject.toml pypix_api/__init__.py CHANGELOG.md uv.lock
git commit -m "🚀 chore: bump version to X.Y.Z"
git push origin main
```

### 6. Criar a tag e disparar o release
```bash
make release-push
```
Cria a tag `vX.Y.Z` (derivada da `version` do `pyproject.toml`) e faz
`git push origin main --tags`, disparando o `release.yml`.

### 7. Monitorar o deploy
Acompanhe em https://github.com/laddertech/pypix-api/actions. Com `gh` autenticado:
```bash
gh run watch
```
- **Prerelease** (`-rc`/`-alpha`/`-beta`): confirme sucesso do `publish-test-pypi`
  (release.yml). O `cd.yml` **não roda**. Valide instalando do Test PyPI:
  `pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pypix-api==X.Y.ZrcN`
  (o `--extra-index-url` pega as dependências reais do PyPI).
- **Produção**: confirme sucesso do `publish-pypi` (release.yml, trusted publishing). O job
  `deploy` do `cd.yml` pode ficar **vermelho** por falta de `PYPI_TOKEN` — é esperado e
  redundante; ignore. O pacote fica em `pip install pypix-api==X.Y.Z`.

## Checklist rápido
- [ ] `main` limpa e sincronizada com `origin`
- [ ] `make test` e `make lint` verdes
- [ ] tipo de bump confirmado com o usuário
- [ ] `pyproject.toml` e `pypix_api/__init__.py` com a **MESMA** versão
- [ ] `CHANGELOG.md` atualizado (Unreleased → X.Y.Z)
- [ ] commit do bump (incluindo `uv.lock`) + `git push origin main`
- [ ] `make release-push` (tag `vX.Y.Z`)
- [ ] workflow de release verde no GitHub Actions
- [ ] pacote instalável: `pip install pypix-api==X.Y.Z`

## Rollback / correção
Não há como despublicar uma versão do PyPI. Se algo sair errado após publicar, o caminho é
**um novo patch** (`X.Y.Z+1`) com a correção. Antes de publicar, prefira validar em
pré-release (`vX.Y.Z-rc1` → Test PyPI) quando houver dúvida.
