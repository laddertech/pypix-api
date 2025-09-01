.PHONY: help build test publish bump-patch bump-minor bump-major pre-commit-install pre-commit-run test-cov test-fast test-unit test-integration coverage-report

help:
	python help.py

## @ Gerenciamento de Pacote Python

sync: ## Sincronizar dependências do projeto
	uv sync
	uv pip install -e ".[dev]"

build: ## Build do pacote
	python -m build

## @ Testes e Cobertura

test: ## Executar testes básicos (mock) sem cobertura
	.venv/bin/pytest tests/tests_mock -v

test-all: ## Executar todos os testes (mock e integração)
	.venv/bin/pytest tests/ -v

test-cov: ## Executar testes com cobertura completa
	.venv/bin/pytest tests/tests_mock --cov=pypix_api --cov-report=html --cov-report=term-missing

test-unit: ## Executar apenas testes unitários/mock
	.venv/bin/pytest tests/tests_mock -v -m "mock or unit"

test-integration: ## Executar apenas testes de integração
	.venv/bin/pytest tests/tests_integration -v -m integration

test-fast: ## Executar testes rápidos (paralelo, sem cobertura)
	.venv/bin/pytest tests/tests_mock -n auto -x --tb=short

coverage-report: ## Gerar relatório de cobertura (HTML)
	.venv/bin/pytest tests/tests_mock --cov=pypix_api --cov-report=html
	@echo "Relatório de cobertura disponível em: coverage_html/index.html"

coverage-check: ## Verificar se cobertura atende mínimo (65%)
	.venv/bin/pytest tests/tests_mock --cov=pypix_api --cov-fail-under=65 --cov-report=term

test-watch: ## Executar testes em modo watch (requer pytest-watch)
	.venv/bin/ptw tests/tests_mock -- -v

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
	.venv/bin/bandit -r pypix_api/ -ll

security-scan: ## Executar scan completo de segurança
	@echo "🔒 Executando scan completo de segurança..."
	@echo "1. Bandit - Python security linter"
	.venv/bin/bandit -r pypix_api/ -ll -f json -o bandit-report.json || true
	@echo "2. Safety - Vulnerability database"
	.venv/bin/pip install --quiet safety
	.venv/bin/safety check --json --output safety-report.json || true
	@echo "3. pip-audit - PyPA vulnerability scanner"
	.venv/bin/pip install --quiet pip-audit
	.venv/bin/pip-audit --desc --format=json --output=pip-audit-report.json || true
	@echo "4. Semgrep - SAST scanner"
	@command -v semgrep >/dev/null 2>&1 && semgrep --config=.semgrep.yml . --json --output=semgrep-report.json || echo "Semgrep not installed, skipping..."
	@echo "✅ Security scan completed! Check *-report.json files for results."

security-report: security-scan ## Gerar relatório de segurança consolidado
	@echo "📊 Gerando relatório consolidado de segurança..."
	@.venv/bin/python -c "import json, os, datetime; print('🔒 Relatório de segurança gerado em:', datetime.datetime.now())"

quality: lint type-check security-check ## Executar todas as verificações de qualidade

quality-full: lint type-check security-check test-cov ## Executar verificações completas (com testes e cobertura)

## @ Documentação

docs: ## Construir documentação com Sphinx
	cd docs && ../.venv/bin/sphinx-build -b html . _build/html

docs-clean: ## Limpar documentação construída
	cd docs && rm -rf _build/

docs-serve: docs ## Servir documentação localmente (requer python -m http.server)
	cd docs/_build/html && python -m http.server 8000

docs-watch: ## Construir documentação em modo watch (requer sphinx-autobuild)
	cd docs && sphinx-autobuild . _build/html --host 0.0.0.0 --port 8000

docs-linkcheck: ## Verificar links na documentação
	cd docs && sphinx-build -b linkcheck . _build/linkcheck
