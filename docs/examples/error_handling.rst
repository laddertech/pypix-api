Tratamento Avancado de Erros
============================

Este guia demonstra como usar o sistema avancado de tratamento de erros da pypix-api
com logging estruturado e metricas integradas.

Configuracao Basica de Observabilidade
--------------------------------------

.. code-block:: python

    import os
    from pypix_api.observability import configure_observability
    from pypix_api.logging import setup_logging
    from pypix_api.error_handling import ErrorHandler, ErrorContext

    # Configurar observabilidade completa
    configure_observability({
        'log_level': 'INFO',
        'log_format': 'json',  # Para producao
        'metrics_enabled': True,
        'error_reporting': True,
        'performance_threshold': 2.0  # Log warning se > 2s
    })

    # Ou configurar apenas logging
    logger = setup_logging(
        level='INFO',
        log_file='pypix_api.log',
        structured=True
    )

Tipos de Erro Especializados
----------------------------

.. code-block:: python

    from pypix_api.error_handling import (
        AuthenticationError,
        ValidationError,
        APIError,
        NetworkError,
        RateLimitError,
        PIXTransactionError
    )

    def exemplo_erros_especializados():
        """Demonstra diferentes tipos de erro."""

        # Erro de autenticacao
        try:
            # Credenciais invalidas
            raise AuthenticationError(
                "Token JWT expirado",
                details={'token_exp': '2025-01-01T00:00:00Z'}
            )
        except AuthenticationError as e:
            print(f"Auth Error: {e.error_code} - {e.message}")
            print(f"Detalhes: {e.details}")

        # Erro de validacao
        try:
            raise ValidationError(
                "CPF invalido",
                field='devedor.cpf',
                details={'value': '12345', 'pattern': r'\d{11}'}
            )
        except ValidationError as e:
            print(f"Campo invalido: {e.details.get('field')}")

        # Erro de API com contexto completo
        try:
            raise APIError(
                "Limite diario excedido",
                status_code=429,
                response_body={'error': 'daily_limit_exceeded', 'limit': 1000},
                details={'endpoint': '/cob', 'method': 'POST'}
            )
        except APIError as e:
            print(f"Status: {e.details['status_code']}")
            print(f"Response: {e.details['response_body']}")

        # Erro de transacao PIX
        try:
            raise PIXTransactionError(
                "Cobranca ja existe",
                txid='TXN123456789',
                operation='criar_cob',
                details={'bank': 'BB', 'duplicate': True}
            )
        except PIXTransactionError as e:
            print(f"TxID: {e.details['txid']}")
            print(f"Operacao: {e.details['operation']}")

Tratamento com Context Manager
------------------------------

.. code-block:: python

    from pypix_api.error_handling import ErrorContext
    from pypix_api.observability import ObservabilityMixin

    class MinhaClasseComObservabilidade(ObservabilityMixin):
        """Exemplo de classe com observabilidade integrada."""

        def __init__(self):
            super().__init__()
            self.bank_name = 'BB'  # Para metricas

        def operacao_com_tratamento_completo(self, txid: str):
            """Operacao com observabilidade completa."""

            # Context manager com observabilidade
            with self.observe_operation('criar_cobranca', txid=txid):

                # Context manager para tratamento de erro
                with ErrorContext('criar_cobranca', {'txid': txid}):

                    # Simulacao de operacao que pode falhar
                    if txid == 'INVALID':
                        raise ValidationError("TxID invalido", field='txid')

                    # Simulacao de chamada API
                    with self.observe_api_call('POST', '/cob'):
                        # Sua logica de API aqui
                        return {'status': 'created', 'txid': txid}

    # Uso da classe
    api = MinhaClasseComObservabilidade()

    try:
        resultado = api.operacao_com_tratamento_completo('TXN123')
        print(f"Sucesso: {resultado}")
    except Exception as e:
        print(f"Erro tratado: {e}")

Tratamento com Decorators
-------------------------

.. code-block:: python

    from pypix_api.error_handling import handle_errors
    from pypix_api.observability import observable_method
    from pypix_api.logging import log_performance

    class APIClient:
        """Cliente API com decorators de observabilidade."""

        @observable_method('autenticar')
        @handle_errors('autenticacao', reraise=True)
        @log_performance(threshold=1.0)
        def autenticar(self, client_id: str, client_secret: str):
            """Autenticacao com observabilidade completa."""

            if not client_id:
                raise AuthenticationError("Client ID obrigatorio")

            if not client_secret:
                raise AuthenticationError("Client Secret obrigatorio")

            # Simulacao de autenticacao
            import time
            time.sleep(0.5)  # Simula latencia

            return {'token': 'jwt_token_123', 'expires_in': 3600}

        @observable_method('criar_cobranca')
        @handle_errors('criar_cobranca')
        def criar_cobranca(self, dados: dict):
            """Criacao de cobranca com retry automatico."""

            from pypix_api.error_handling import ErrorRecovery

            def _criar_cobranca():
                # Validacao
                if not dados.get('valor'):
                    raise ValidationError("Valor obrigatorio", field='valor')

                if not dados.get('chave'):
                    raise ValidationError("Chave PIX obrigatoria", field='chave')

                # Simulacao de falha de rede (para demonstrar retry)
                import random
                if random.random() < 0.3:
                    raise NetworkError("Falha de conexao temporaria")

                return {'txid': 'TXN123456', 'status': 'created'}

            # Retry automatico com backoff
            return ErrorRecovery.retry_with_backoff(_criar_cobranca, max_retries=3)

Exemplo Completo com Banco do Brasil
------------------------------------

.. code-block:: python

    import os
    import uuid
    from datetime import datetime
    from typing import Dict, Any

    from pypix_api.auth.oauth2 import OAuth2Client
    from pypix_api.banks.bb import BBPixAPI
    from pypix_api.observability import configure_observability, create_observability_report
    from pypix_api.error_handling import (
        ErrorContext, ErrorRecovery,
        AuthenticationError, ValidationError, APIError
    )

    class ObservableBBPixAPI(BBPixAPI):
        """BB PIX API com observabilidade completa."""

        def __init__(self, *args, **kwargs):
            """Initialize with observability."""
            # Configurar observabilidade antes de inicializar
            configure_observability({
                'log_level': 'INFO',
                'log_format': 'json',
                'metrics_enabled': True,
                'error_reporting': True
            })

            super().__init__(*args, **kwargs)

            # Adicionar observabilidade
            from pypix_api.observability import ObservabilityMixin
            ObservabilityMixin.__init__(self)

        def criar_cobranca_observavel(self, txid: str, dados: Dict[str, Any]) -> Dict:
            """Criar cobranca com observabilidade completa."""

            with self.observe_operation('criar_cobranca_bb', txid=txid):

                # Validacao com contexto de erro
                with ErrorContext('validacao_dados', {'txid': txid}):
                    self._validar_dados_cobranca(dados)

                # Autenticacao com retry
                with ErrorContext('autenticacao', {'txid': txid}):
                    token = self._obter_token_com_retry()

                # Chamada API com observabilidade
                with self.observe_api_call('POST', f'/cob/{txid}', body=dados):
                    return self._fazer_chamada_api('POST', f'/cob/{txid}', dados)

        def _validar_dados_cobranca(self, dados: Dict[str, Any]):
            """Validacao detalhada com erros especificos."""

            if not dados.get('calendario'):
                raise ValidationError(
                    "Campo calendario obrigatorio",
                    field='calendario'
                )

            if not dados.get('devedor'):
                raise ValidationError(
                    "Campo devedor obrigatorio",
                    field='devedor'
                )

            devedor = dados['devedor']
            if not devedor.get('nome'):
                raise ValidationError(
                    "Nome do devedor obrigatorio",
                    field='devedor.nome'
                )

            # Validacao CPF/CNPJ
            if not devedor.get('cpf') and not devedor.get('cnpj'):
                raise ValidationError(
                    "CPF ou CNPJ obrigatorio",
                    field='devedor',
                    details={'missing': ['cpf', 'cnpj']}
                )

            if 'cpf' in devedor:
                cpf = devedor['cpf'].replace('.', '').replace('-', '')
                if len(cpf) != 11 or not cpf.isdigit():
                    raise ValidationError(
                        "CPF deve ter 11 digitos numericos",
                        field='devedor.cpf',
                        details={'value': devedor['cpf'], 'length': len(cpf)}
                    )

            # Validacao valor
            valor = dados.get('valor', {})
            if not valor.get('original'):
                raise ValidationError(
                    "Valor original obrigatorio",
                    field='valor.original'
                )

            try:
                valor_num = float(valor['original'])
                if valor_num <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                raise ValidationError(
                    "Valor deve ser numerico e positivo",
                    field='valor.original',
                    details={'value': valor.get('original')}
                )

        def _obter_token_com_retry(self) -> str:
            """Obter token com retry automatico."""

            def _obter_token():
                try:
                    return self.oauth.get_token()
                except Exception as e:
                    if 'invalid_client' in str(e):
                        raise AuthenticationError(
                            "Credenciais invalidas",
                            details={'client_id': self.oauth.client_id}
                        )
                    elif 'certificate' in str(e).lower():
                        raise AuthenticationError(
                            "Erro no certificado",
                            details={'cert_path': self.oauth.cert_path}
                        )
                    else:
                        raise NetworkError(f"Falha na autenticacao: {e}")

            return ErrorRecovery.retry_with_backoff(
                _obter_token,
                max_retries=3,
                base_delay=2.0
            )

        def _fazer_chamada_api(self, method: str, endpoint: str, dados: Dict) -> Dict:
            """Fazer chamada API com tratamento completo de erros."""

            def _chamada():
                # Simulacao de chamada API
                response = self.session.request(method, endpoint, json=dados)

                if response.status_code == 401:
                    raise AuthenticationError(
                        "Token expirado ou invalido",
                        details={'status_code': response.status_code}
                    )
                elif response.status_code == 400:
                    raise ValidationError(
                        "Dados invalidos",
                        details={
                            'status_code': response.status_code,
                            'response': response.json()
                        }
                    )
                elif response.status_code == 429:
                    raise RateLimitError(
                        "Rate limit excedido",
                        retry_after=int(response.headers.get('Retry-After', 60)),
                        details={'status_code': response.status_code}
                    )
                elif response.status_code >= 500:
                    raise APIError(
                        "Erro interno do servidor",
                        status_code=response.status_code,
                        response_body=response.json()
                    )
                elif not response.ok:
                    raise APIError(
                        f"Erro HTTP {response.status_code}",
                        status_code=response.status_code,
                        response_body=response.json()
                    )

                return response.json()

            return ErrorRecovery.retry_with_backoff(_chamada, max_retries=2)

    def exemplo_uso_completo():
        """Exemplo de uso completo com observabilidade."""

        # Configuracao OAuth2
        oauth = OAuth2Client(
            client_id=os.getenv('BB_CLIENT_ID'),
            client_secret=os.getenv('BB_CLIENT_SECRET'),
            cert_path=os.getenv('BB_CERT_PATH'),
            cert_password=os.getenv('BB_CERT_PASSWORD'),
            scope='cob.write cob.read'
        )

        # API com observabilidade
        api = ObservableBBPixAPI(oauth=oauth, sandbox_mode=True)

        # Dados da cobranca
        txid = str(uuid.uuid4())
        cobranca = {
            'calendario': {'expiracao': 3600},
            'devedor': {
                'cpf': '12345678901',
                'nome': 'Cliente Teste'
            },
            'valor': {'original': '100.50'},
            'chave': 'empresa@email.com',
            'solicitacaoPagador': 'Teste com observabilidade'
        }

        try:
            # Operacao com observabilidade completa
            resultado = api.criar_cobranca_observavel(txid, cobranca)

            print(f"✅ Cobranca criada: {resultado['txid']}")

        except ValidationError as e:
            print(f"❌ Dados invalidos: {e.message}")
            print(f"Campo: {e.details.get('field')}")

        except AuthenticationError as e:
            print(f"🔐 Erro de autenticacao: {e.message}")
            print(f"Client ID: {e.details.get('client_id')}")

        except RateLimitError as e:
            print(f"⏳ Rate limit excedido: {e.message}")
            print(f"Retry after: {e.details.get('retry_after')}s")

        except APIError as e:
            print(f"🌐 Erro da API: {e.message}")
            print(f"Status: {e.details.get('status_code')}")

        except Exception as e:
            print(f"💥 Erro inesperado: {e}")

        finally:
            # Relatorio de observabilidade
            relatorio = create_observability_report()

            print("\n📊 Relatorio de Observabilidade:")
            print(f"Status: {relatorio['health']['status']}")
            print(f"Total API calls: {relatorio['metrics_summary']['total_api_calls']}")
            print(f"Error rate: {relatorio['metrics_summary']['error_rate']:.2%}")

    if __name__ == '__main__':
        exemplo_uso_completo()

Health Check e Monitoramento
----------------------------

.. code-block:: python

    from pypix_api.observability import get_observability_status, HealthCheck

    def monitoramento_sistema():
        """Exemplo de monitoramento do sistema."""

        # Health check completo
        health = get_observability_status()

        print(f"Status geral: {health['status']}")

        for check_name, result in health['checks'].items():
            status = "✅" if result['healthy'] else "❌"
            print(f"{status} {check_name}: {result}")

        # Health check customizado
        health_checker = HealthCheck()

        # Adicionar verificacoes customizadas
        def verificar_conectividade_bb():
            """Verificar conectividade com Banco do Brasil."""
            try:
                import requests
                response = requests.head('https://api.bb.com.br', timeout=5)
                return response.status_code < 500
            except:
                return False

        conectividade_ok = verificar_conectividade_bb()
        print(f"{'✅' if conectividade_ok else '❌'} Conectividade BB: {conectividade_ok}")

Configuracao para Producao
--------------------------

.. code-block:: python

    # config/observability.py
    OBSERVABILITY_CONFIG = {
        # Logging
        'log_level': 'WARNING',  # Menos verbose em producao
        'log_format': 'json',    # Estruturado para agregadores
        'log_file': '/var/log/pypix-api/app.log',

        # Metricas
        'metrics_enabled': True,
        'metrics_export_path': '/var/log/pypix-api/metrics.jsonl',
        'metrics_flush_interval': 60,  # Flush a cada minuto

        # Error handling
        'error_reporting': True,
        'detailed_tracebacks': False,  # Sem stack traces em producao

        # Performance
        'performance_threshold': 5.0,  # Alert se > 5s
        'track_all_methods': False     # Track apenas metodos importantes
    }

    # Em seu app principal
    from pypix_api.observability import configure_observability

    configure_observability(OBSERVABILITY_CONFIG)

Integracao com Sistemas de Monitoramento
----------------------------------------

.. code-block:: python

    import json
    from pypix_api.metrics import export_metrics
    from pypix_api.observability import create_observability_report

    # Exportar para Prometheus (formato customizado)
    def exportar_prometheus():
        """Exportar metricas no formato Prometheus."""
        relatorio = create_observability_report()

        # Converter metricas para formato Prometheus
        metricas_prometheus = []

        for metric in relatorio.get('metrics_summary', {}).items():
            linha = f"pypix_api_{metric[0]} {metric[1]}"
            metricas_prometheus.append(linha)

        # Salvar em arquivo
        with open('/var/lib/pypix-api/metrics.prom', 'w') as f:
            f.write('\n'.join(metricas_prometheus))

    # Webhook para alertas
    def enviar_alerta_slack(error_info):
        """Enviar alerta para Slack quando erro critico ocorrer."""
        import requests

        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        if not webhook_url:
            return

        payload = {
            'text': f"🚨 Erro critico na pypix-api: {error_info['message']}",
            'attachments': [{
                'color': 'danger',
                'fields': [
                    {'title': 'Error Code', 'value': error_info.get('error_code'), 'short': True},
                    {'title': 'Timestamp', 'value': error_info.get('timestamp'), 'short': True}
                ]
            }]
        }

        requests.post(webhook_url, json=payload)

Proximos Passos
--------------

- Configurar alertas baseados em metricas
- Integrar com sistemas de APM (DataDog, New Relic)
- Implementar dashboards customizados
- Configurar log aggregation (ELK Stack)
