.PHONY: help build test publish bump-patch bump-minor bump-major pre-commit-install pre-commit-run

help:
	python help.py

## @ Gerenciamento de Pacote Python

sync: ## Sincronizar dependências do projeto
	uv sync
	uv pip install -e ".[dev]"

build: ## Build do pacote
	python -m build

test: ## Executar testes
	pytest tests/tests_mock

publish: build ## Publicar no PyPI (requer TWINE_USERNAME e TWINE_PASSWORD)
	twine upload dist/*

clean: ## Limpar builds anteriores
	rm -rf dist/ build/ *.egg-info/

## @ Atualiza versão do pacote

bump-patch: ## Incrementar versão (patch)
	python scripts/bump_version.py patch

bump-minor: ## Incrementar versão (minor)
	python scripts/bump_version.py minor

bump-major: ## Incrementar versão (major)
	python scripts/bump_version.py major

## @ Verifica e formata código

lint: ## Verificar estilo de código
	ruff check .

format: ## Formatar código
	ruff format .

fix: ## Corrigir problemas de estilo de código
	ruff check . --fix
	ruff format .

## @ Pre-commit hooks

pre-commit-install: ## Instalar pre-commit hooks
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "Pre-commit hooks instalados com sucesso!"

pre-commit-run: ## Executar pre-commit em todos os arquivos
	pre-commit run --all-files

pre-commit-update: ## Atualizar versões dos hooks
	pre-commit autoupdate

## @ Qualidade de código

type-check: ## Verificar tipos com mypy
	mypy pypix_api/

security-check: ## Verificar segurança com bandit
	bandit -r pypix_api/ -ll

quality: lint type-check security-check ## Executar todas as verificações de qualidade
