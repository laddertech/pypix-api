# Guia de Type Checking para pypix-api

## O que é Type Checking?

Type checking é a verificação estática de tipos em Python usando ferramentas como MyPy. Ajuda a detectar erros de tipo antes da execução, melhorando a qualidade e manutenibilidade do código.

## Status Atual

✅ **Implementado com sucesso!**
- Arquivo `py.typed` presente (marca o pacote como compatível com type hints)
- MyPy configurado no `pyproject.toml`
- Type hints básicos adicionados nas classes principais
- Todos os erros de tipo corrigidos

## Executando Type Check

### Comando Rápido
```bash
make type-check
```

### Comando Manual
```bash
.venv/bin/mypy pypix_api/
```

### Verificar arquivo específico
```bash
.venv/bin/mypy pypix_api/banks/base.py
```

## Configuração Atual (Permissiva)

O MyPy está configurado de forma permissiva para facilitar a adoção gradual:

```toml
[tool.mypy]
python_version = "3.10"
disallow_untyped_defs = false  # Não exige tipos em todas as funções
check_untyped_defs = false      # Não verifica funções sem tipos
ignore_missing_imports = true   # Ignora bibliotecas sem stubs
disable_error_code = ["attr-defined", "no-any-return", "has-type"]
```

## Guia de Type Hints

### Imports Necessários
```python
from typing import Any, Dict, List, Optional, Union, Tuple
```

### Exemplos Básicos

#### Variáveis
```python
# Simples
name: str = "pypix-api"
count: int = 42
is_active: bool = True

# Com Optional (pode ser None)
token: Optional[str] = None
client_id: Optional[str] = os.getenv('CLIENT_ID')

# Dicionários e Listas
headers: Dict[str, str] = {'Content-Type': 'application/json'}
scopes: List[str] = ['pix.read', 'pix.write']
cache: Dict[str, Dict[str, Any]] = {}
```

#### Funções
```python
# Função simples
def get_bank_code(self) -> str:
    return '001'

# Com parâmetros tipados
def get_token(self, scope: str) -> str:
    return self.token_cache[scope]

# Com Optional
def find_user(self, user_id: int) -> Optional[Dict[str, Any]]:
    return self.users.get(user_id)

# Com Union (múltiplos tipos)
def process_data(self, data: Union[str, bytes]) -> Dict[str, Any]:
    # processa dados
    return result
```

#### Classes
```python
class OAuth2Client:
    # Atributos de classe
    token_url: str
    client_id: Optional[str]
    session: requests.Session
    token_cache: Dict[str, Dict[str, Any]]

    def __init__(
        self,
        token_url: str,
        client_id: Optional[str] = None,
        sandbox_mode: bool = False
    ) -> None:
        self.token_url = token_url
        self.client_id = client_id
        self.sandbox_mode = sandbox_mode
```

## Problemas Comuns e Soluções

### 1. Conversão de Tipos em Dicionários
```python
# ❌ Errado - int para str implícito
params['page'] = page_number  # page_number é int

# ✅ Correto - conversão explícita
params['page'] = str(page_number)
```

### 2. Optional vs Union
```python
# Para valores que podem ser None
token: Optional[str] = None  # Equivale a Union[str, None]

# Para múltiplos tipos possíveis
data: Union[str, bytes, BinaryIO]
```

### 3. Type Hints em Mixins
```python
# Use Protocol para definir interface esperada
from typing import Protocol

class PixAPIProtocol(Protocol):
    session: requests.Session
    def _create_headers(self) -> Dict[str, str]: ...
    def get_base_url(self) -> str: ...
```

### 4. Ignorar Erros Específicos
```python
# Para uma linha específica
result = untypable_function()  # type: ignore

# Para um arquivo inteiro (no topo)
# mypy: ignore-errors
```

## Evolução Gradual

### Fase 1 (Atual) ✅
- Configuração permissiva
- Type hints básicos
- Correção de erros óbvios

### Fase 2 (Recomendado)
Ative verificações mais rigorosas gradualmente:
```toml
disallow_untyped_defs = true    # Exige tipos em funções
check_untyped_defs = true        # Verifica funções sem tipos
warn_return_any = true           # Avisa sobre Any em returns
```

### Fase 3 (Avançado)
```toml
strict = true                    # Modo strict completo
disallow_any_generics = true    # Proíbe Any em genéricos
warn_redundant_casts = true     # Avisa casts desnecessários
```

## Integração com IDE

### VS Code
Instale a extensão Pylance para suporte completo a type hints.

### PyCharm
Suporte nativo, ative em: Settings → Editor → Inspections → Python → Type checker

## Benefícios

1. **Detecção precoce de erros**: Encontra bugs antes da execução
2. **Melhor documentação**: Types servem como documentação inline
3. **Autocomplete aprimorado**: IDEs fornecem sugestões mais precisas
4. **Refatoração segura**: Mudanças detectam incompatibilidades
5. **Código mais robusto**: Força pensar sobre tipos e interfaces

## Comandos Úteis

```bash
# Verificar tipos
make type-check

# Gerar relatório de cobertura de tipos
.venv/bin/mypy pypix_api/ --html-report mypy-report

# Verificar com modo strict (experimental)
.venv/bin/mypy pypix_api/ --strict

# Mostrar apenas erros (sem notas)
.venv/bin/mypy pypix_api/ --no-error-summary
```

## Recursos Adicionais

- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 561 - Distributing Type Information](https://peps.python.org/pep-0561/)

## Próximos Passos

1. Continue adicionando type hints em novos códigos
2. Gradualmente adicione tipos em código existente
3. Ative verificações mais rigorosas conforme o time se adapta
4. Considere usar `pydantic` para validação runtime de tipos
