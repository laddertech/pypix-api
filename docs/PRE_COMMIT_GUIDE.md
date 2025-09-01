# Guia do Pre-commit para pypix-api

## O que é Pre-commit?

Pre-commit é uma ferramenta que executa verificações automáticas no seu código antes de cada commit, garantindo qualidade e consistência.

## Instalação Rápida

```bash
# Método 1: Usando o Makefile
make pre-commit-install

# Método 2: Usando o script
./scripts/setup_pre_commit.sh

# Método 3: Manual
.venv/bin/pre-commit install
```

## Hooks Configurados

### ✅ Ativos (Executam automaticamente)

1. **Formatação e Limpeza**
   - `trailing-whitespace`: Remove espaços em branco no final das linhas
   - `end-of-file-fixer`: Garante que arquivos terminem com nova linha
   - `check-docstring-first`: Verifica se docstrings vêm antes do código

2. **Validação de Sintaxe**
   - `check-yaml`: Valida arquivos YAML
   - `check-toml`: Valida arquivos TOML
   - `check-json`: Valida arquivos JSON (exceto .vscode e .devcontainer)
   - `check-merge-conflict`: Detecta marcadores de conflito do git

3. **Segurança Básica**
   - `detect-private-key`: Detecta chaves privadas acidentais
   - `check-added-large-files`: Previne commit de arquivos grandes (>1MB)

4. **Qualidade Python**
   - `ruff`: Linting básico (erros, warnings, imports)
   - `ruff-format`: Formatação automática do código
   - `check-no-print`: Detecta prints esquecidos no código

### 🔧 Desativados (Executar manualmente)

Estes hooks estão comentados para evitar fricção inicial, mas podem ser executados manualmente:

```bash
# Type checking
make type-check

# Security scanning
make security-check

# Todas as verificações de qualidade
make quality
```

## Comandos Úteis

### Executar em todos os arquivos
```bash
make pre-commit-run
# ou
.venv/bin/pre-commit run --all-files
```

### Executar em arquivos específicos
```bash
.venv/bin/pre-commit run --files pypix_api/banks/base.py
```

### Atualizar versões dos hooks
```bash
make pre-commit-update
# ou
.venv/bin/pre-commit autoupdate
```

### Pular hooks temporariamente
```bash
git commit --no-verify -m "mensagem do commit"
```

## Workflow Recomendado

1. **Fazer suas alterações normalmente**
2. **Adicionar arquivos ao stage**: `git add .`
3. **Tentar commit**: `git commit -m "sua mensagem"`
4. **Se houver falhas**:
   - Verifique os erros reportados
   - Corrija os problemas ou aceite as correções automáticas
   - Adicione as correções: `git add .`
   - Tente o commit novamente

## Resolução de Problemas

### Hook falha com "command not found"
```bash
# Reinstalar dependências
uv sync
uv pip install -e ".[dev]"
make pre-commit-install
```

### Desabilitar hook específico temporariamente
Edite `.pre-commit-config.yaml` e comente o hook problemático.

### Limpar cache do pre-commit
```bash
.venv/bin/pre-commit clean
```

## Configuração Progressiva

### Fase 1 (Atual) - Básico
- Formatação e limpeza automática
- Validação de sintaxe
- Detecção de problemas óbvios

### Fase 2 (Recomendado após estabilização)
Descomente no `.pre-commit-config.yaml`:
- MyPy para type checking
- Bandit para análise de segurança

### Fase 3 (Avançado)
- Adicionar pytest nos hooks
- Adicionar verificação de cobertura
- Integrar com CI/CD

## Benefícios

1. **Consistência**: Todo código segue o mesmo padrão
2. **Qualidade**: Problemas detectados antes do commit
3. **Economia de tempo**: Menos revisões de código para formatação
4. **Segurança**: Previne commit de segredos e vulnerabilidades
5. **Aprendizado**: Ajuda a escrever código melhor

## Próximos Passos

Após se acostumar com os hooks básicos:

1. Execute `make quality` regularmente para verificações completas
2. Considere ativar MyPy para type checking
3. Configure seu editor para usar Ruff automaticamente
4. Integre as mesmas verificações no CI/CD
