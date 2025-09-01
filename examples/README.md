# pypix-api Examples

Esta pasta contém exemplos práticos de como usar a biblioteca pypix-api em diferentes cenários.

## 📁 Arquivos de Exemplo

### `observability_demo.py`

Demonstração completa do sistema de observabilidade da pypix-api, incluindo:

- **Logging estruturado** com diferentes níveis e formatos
- **Métricas em tempo real** de performance e uso
- **Tratamento avançado de erros** com classificação automática
- **Retry automático** com backoff exponencial
- **Health checks** e monitoramento do sistema
- **Exportação de métricas** para análise

**Como executar:**

```bash
# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Executar demo
python examples/observability_demo.py
```

**Saída esperada:**

```
🚀 Demonstração de Observabilidade pypix-api
==================================================

1️⃣ Configurando observabilidade...

2️⃣ Verificando status do sistema...
Status geral: healthy (✅)
  ✅ logging: OK
  ✅ metrics: OK
  ✅ error_handling: OK
  ✅ memory: OK

3️⃣ Inicializando API com observabilidade...

4️⃣ Executando operações com observabilidade...
  ✅ Cobrança 1: DEMO-A1B2C3D4 - ATIVA
  ❌ Cobrança 2: Validação - CPF invalido
  ✅ Cobrança 3: DEMO-E5F6G7H8 - ATIVA
  🌐 Cobrança 4: API 429 - Rate limit excedido
  ...

📊 Resumo de métricas coletadas:
  Total de métricas: 45
  Chamadas de API: 8
  Taxa de erro: 20.0%
  Tempo médio de resposta: 0.456s
```

## 🔧 Configuração para Diferentes Ambientes

### Desenvolvimento

```python
from pypix_api import configure_observability

configure_observability({
    'log_level': 'DEBUG',
    'log_format': 'text',
    'metrics_enabled': True,
    'error_reporting': True,
    'performance_threshold': 0.5
})
```

### Produção

```python
configure_observability({
    'log_level': 'WARNING',
    'log_format': 'json',
    'metrics_enabled': True,
    'metrics_export_path': '/var/log/pypix/metrics.jsonl',
    'error_reporting': True,
    'detailed_tracebacks': False
})
```

## 🎯 Cenários de Uso

### 1. Monitoramento Básico

```python
from pypix_api import PIXLogger, get_metrics_summary

logger = PIXLogger('minha_app')
logger.info("Operação iniciada", operation='criar_cobranca')

# Verificar métricas
metrics = get_metrics_summary()
print(f"API calls: {metrics['total_api_calls']}")
```

### 2. Tratamento de Erros Robusto

```python
from pypix_api.error_handling import ErrorContext, ValidationError

with ErrorContext('criar_cobranca', {'txid': 'ABC123'}):
    if not dados['valor']:
        raise ValidationError("Valor obrigatório", field='valor')
```

### 3. Tracking de Performance

```python
from pypix_api.observability import PerformanceTracker

with PerformanceTracker('operacao_complexa'):
    # Sua operação aqui
    resultado = fazer_operacao_complexa()
```

## 📊 Métricas Disponíveis

A biblioteca coleta automaticamente as seguintes métricas:

- **api_calls_total** - Total de chamadas para APIs bancárias
- **api_call_duration** - Tempo de resposta das APIs
- **api_errors_total** - Total de erros por tipo
- **function.{nome}.calls** - Chamadas de função específica
- **function.{nome}.duration** - Duração de execução
- **bank_operation.{banco}.{operacao}** - Operações por banco

## 🚨 Alertas e Monitoramento

### Configurar Alertas Básicos

```python
from pypix_api.observability import HealthCheck

health = HealthCheck()
status = health.check_system_health()

if status['status'] != 'healthy':
    # Enviar alerta
    print(f"🚨 Sistema não saudável: {status}")
```

### Integração com Sistemas Externos

```python
# Exportar métricas para Prometheus
from pypix_api.metrics import export_metrics
export_metrics('/var/lib/node_exporter/pypix_metrics.prom')

# Webhook para Slack/Teams
def send_alert(error_info):
    import requests
    webhook_url = os.getenv('WEBHOOK_URL')
    payload = {'text': f'Erro crítico: {error_info}'}
    requests.post(webhook_url, json=payload)
```

## 🔍 Debugging Avançado

### Logs Estruturados

```python
# Configurar logging estruturado
import os
os.environ['PYPIX_LOG_FORMAT'] = 'json'

# Logs serão em formato JSON
{
  "timestamp": "2025-01-15T10:30:00.123Z",
  "level": "ERROR",
  "logger": "pypix_api.api",
  "message": "API call failed",
  "request_id": "req-123",
  "status_code": 500,
  "error_type": "APIError"
}
```

### Análise de Performance

```python
# Identificar operações lentas
metrics = get_metrics_summary()
slow_operations = [
    op for op in metrics.get('histograms', {})
    if 'duration' in op and max(op['values']) > 2.0
]
```

## 📝 Logs de Exemplo

### Sucesso
```
2025-01-15 10:30:00 - pypix_api.banks.bb - INFO - Cobrança criada com sucesso
  txid: TXN123456789
  status: ATIVA
  response_time: 0.234s
```

### Erro com Context
```
2025-01-15 10:30:15 - pypix_api.error - ERROR - API Error: 400
  operation: criar_cobranca
  txid: TXN987654321
  error_code: VALIDATION_ERROR
  field: devedor.cpf
  details: {"value": "123", "expected_length": 11}
```

## 🎯 Próximos Passos

1. **Configurar agregação de logs** (ELK Stack, Fluentd)
2. **Implementar dashboards** (Grafana, Kibana)
3. **Configurar alertas automáticos** (PagerDuty, OpsGenie)
4. **Integrar APM** (DataDog, New Relic, Dynatrace)

## 📚 Documentação Adicional

- [Guia de Error Handling](../docs/examples/error_handling.rst)
- [Configuração de Webhooks](../docs/examples/webhooks.rst)
- [Documentação completa](../docs/)
