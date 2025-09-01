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

## @ Releases e versionamento

version: ## Mostrar versão atual
	python scripts/release.py --current

release-patch: ## Preparar release patch (0.5.0 -> 0.5.1)
	python scripts/release.py patch

release-minor: ## Preparar release minor (0.5.0 -> 0.6.0)
	python scripts/release.py minor

release-major: ## Preparar release major (0.5.0 -> 1.0.0)
	python scripts/release.py major

release-prerelease: ## Preparar pre-release (ex: 0.5.1-alpha)
	@read -p "Tipo de bump (patch/minor/major): " bump_type; \
	read -p "Sufixo do pre-release (alpha/beta/rc1): " suffix; \
	python scripts/release.py $$bump_type --pre $$suffix

release-dry-run: ## Simular release sem fazer mudanças
	@read -p "Tipo de bump (patch/minor/major): " bump_type; \
	python scripts/release.py $$bump_type --dry-run

# Legacy aliases for backward compatibility
bump-patch: release-patch
bump-minor: release-minor
bump-major: release-major

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

docs-api: ## Gerar documentação da API automaticamente
	cd docs && sphinx-apidoc -o api/ ../pypix_api/ --force --module-first

docs-full: docs-api docs ## Construir documentação completa (API + manual)

docs-github: docs-full ## Preparar documentação para GitHub Pages
	@echo "📚 Documentação preparada para GitHub Pages em: docs/_build/html/"
	@echo "🌐 URL local para testar: file://$(PWD)/docs/_build/html/index.html"

## @ Testes multi-ambiente e benchmarks

tox: ## Executar testes em múltiplas versões do Python
	tox

tox-clean: ## Limpar ambientes tox
	tox -e clean
	rm -rf .tox/

tox-py310: ## Executar testes apenas no Python 3.10
	tox -e py310

tox-py311: ## Executar testes apenas no Python 3.11
	tox -e py311

tox-py312: ## Executar testes apenas no Python 3.12
	tox -e py312

tox-integration: ## Executar testes de integração em múltiplos ambientes
	tox -e py310-integration,py311-integration,py312-integration

tox-security: ## Executar scan de segurança via tox
	tox -e security

tox-docs: ## Construir documentação via tox
	tox -e docs

benchmark: ## Executar benchmarks de performance
	tox -e benchmark

benchmark-local: ## Executar benchmarks localmente
	.venv/bin/pytest tests/benchmarks -v --benchmark-only

benchmark-compare: ## Executar benchmarks e salvar para comparação
	.venv/bin/pytest tests/benchmarks --benchmark-autosave --benchmark-only

benchmark-report: ## Gerar relatório de benchmark
	.venv/bin/pytest tests/benchmarks --benchmark-only --benchmark-json=benchmark-report.json
