#!/bin/bash

# Script para configurar pre-commit hooks no projeto pypix-api
# Este script instala as dependências necessárias e configura os hooks

set -e  # Exit on error

echo "🔧 Configurando Pre-commit Hooks para pypix-api..."
echo "================================================"

# Verificar se estamos no diretório correto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Erro: Este script deve ser executado na raiz do projeto pypix-api"
    exit 1
fi

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: Python 3 não está instalado"
    exit 1
fi

echo "📦 Instalando dependências de desenvolvimento..."
# Instalar dependências de desenvolvimento
if command -v uv &> /dev/null; then
    echo "   Usando uv para instalar dependências..."
    uv pip install -e ".[dev]"
else
    echo "   Usando pip para instalar dependências..."
    pip install -e ".[dev]"
fi

echo ""
echo "🎣 Instalando pre-commit hooks..."
# Instalar pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg

echo ""
echo "🔍 Verificando instalação..."
# Verificar se os hooks foram instalados
if [ -f ".git/hooks/pre-commit" ]; then
    echo "✅ Pre-commit hook instalado com sucesso"
else
    echo "⚠️  Aviso: Pre-commit hook pode não ter sido instalado corretamente"
fi

echo ""
echo "📋 Hooks configurados:"
echo "   - trailing-whitespace: Remove espaços em branco no final das linhas"
echo "   - end-of-file-fixer: Garante que arquivos terminem com nova linha"
echo "   - check-yaml: Valida sintaxe YAML"
echo "   - check-json: Valida sintaxe JSON"
echo "   - check-toml: Valida sintaxe TOML"
echo "   - check-added-large-files: Previne commit de arquivos grandes"
echo "   - detect-private-key: Detecta chaves privadas"
echo "   - ruff: Linting e formatação de código Python"
echo "   - mypy: Verificação de tipos"
echo "   - bandit: Análise de segurança"
echo "   - detect-secrets: Detecção de segredos no código"

echo ""
echo "🚀 Comandos úteis:"
echo "   make pre-commit-run    # Executar hooks em todos os arquivos"
echo "   make pre-commit-update # Atualizar versões dos hooks"
echo "   make quality          # Executar todas as verificações de qualidade"

echo ""
echo "✨ Pre-commit configurado com sucesso!"
echo ""
echo "💡 Dica: Os hooks serão executados automaticamente antes de cada commit."
echo "   Para pular os hooks temporariamente, use: git commit --no-verify"
echo ""
