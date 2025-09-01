Cobran�as com Vencimento
========================

Este guia mostra como criar e gerenciar cobran�as PIX com data de vencimento.

Cobran�a com Vencimento Simples
-------------------------------

.. code-block:: python

    import uuid
    from datetime import datetime, timedelta
    from pypix_api.auth.oauth2 import OAuth2Client
    from pypix_api.banks.bb import BBPixAPI

    oauth = OAuth2Client(
        client_id='seu_client_id',
        client_secret='seu_client_secret',
        cert_path='certificado.p12',
        cert_password='senha_cert',
        scope='cobv.write cobv.read'
    )

    api = BBPixAPI(oauth=oauth)

    def criar_cobranca_com_vencimento():
        """Cria cobran�a PIX com data de vencimento."""

        txid = str(uuid.uuid4())
        vencimento = datetime.now() + timedelta(days=7)

        cobranca = {
            'calendario': {
                'dataDeVencimento': vencimento.strftime('%Y-%m-%d'),
                'validadeAposVencimento': 30
            },
            'devedor': {
                'cpf': '12345678901',
                'nome': 'Cliente Mensal'
            },
            'valor': {
                'original': '299.90'
            },
            'chave': 'empresa@email.com',
            'solicitacaoPagador': 'Mensalidade - Janeiro 2025'
        }

        resultado = api.criar_cobv(txid, cobranca)
        print(f"=� Cobran�a criada: {resultado['txid']}")
        return resultado

Cobran�a Recorrente Mensal
--------------------------

.. code-block:: python

    class CobrancaRecorrente:
        """Gerenciador de cobran�as recorrentes."""

        def __init__(self, api):
            self.api = api

        def criar_cobranca_mensal(self, cliente_dados, valor, referencia):
            """Cria cobran�a mensal para um cliente."""

            hoje = datetime.now()
            vencimento = hoje + timedelta(days=30)  # Vence em 30 dias

            txid = f"MENSAL-{cliente_dados['cpf']}-{vencimento.strftime('%Y%m')}"

            cobranca = {
                'calendario': {
                    'dataDeVencimento': vencimento.strftime('%Y-%m-%d'),
                    'validadeAposVencimento': 30
                },
                'devedor': cliente_dados,
                'valor': {
                    'original': str(valor)
                },
                'chave': 'cobranca@empresa.com',
                'solicitacaoPagador': f'Mensalidade - {referencia}'
            }

            try:
                resultado = self.api.criar_cobv(txid, cobranca)
                print(f" Mensalidade criada: {cliente_dados['nome']}")
                return resultado
            except Exception as e:
                print(f"L Erro: {e}")
                return None

Exemplo de Uso
--------------

.. code-block:: python

    def exemplo_cobrancas_mensais():
        """Exemplo completo de cobran�as mensais."""

        clientes = [
            {
                'cpf': '12345678901',
                'nome': 'Jo�o Silva'
            },
            {
                'cpf': '98765432100',
                'nome': 'Maria Santos'
            }
        ]

        gerenciador = CobrancaRecorrente(api)

        for cliente in clientes:
            gerenciador.criar_cobranca_mensal(
                cliente,
                150.00,
                'Janeiro/2025'
            )

Monitoramento de Cobran�as
--------------------------

.. code-block:: python

    def monitorar_cobrancas():
        """Monitora status das cobran�as."""

        inicio = datetime.now() - timedelta(days=30)
        fim = datetime.now()

        cobrancas = api.consultar_cobvs(
            data_inicio=inicio.strftime('%Y-%m-%dT%H:%M:%S-03:00'),
            data_fim=fim.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        )

        for cob in cobrancas.get('cobs', []):
            status = cob['status']
            valor = cob['valor']['original']

            if status == 'ATIVA':
                print(f"� Pendente: R$ {valor}")
            elif status == 'CONCLUIDA':
                print(f" Paga: R$ {valor}")

Script Completo
---------------

.. code-block:: python

    #!/usr/bin/env python3
    """Sistema de cobran�as recorrentes."""

    import os
    from datetime import datetime
    from pypix_api.auth.oauth2 import OAuth2Client
    from pypix_api.banks.bb import BBPixAPI

    def main():
        oauth = OAuth2Client(
            client_id=os.getenv('BB_CLIENT_ID'),
            client_secret=os.getenv('BB_CLIENT_SECRET'),
            cert_path=os.getenv('BB_CERT_PATH'),
            cert_password=os.getenv('BB_CERT_PASSWORD'),
            scope='cobv.write cobv.read'
        )

        api = BBPixAPI(oauth=oauth)
        gerenciador = CobrancaRecorrente(api)

        # Processar cobran�as
        clientes = [{'cpf': '12345678901', 'nome': 'Cliente Teste'}]

        for cliente in clientes:
            gerenciador.criar_cobranca_mensal(
                cliente,
                99.90,
                datetime.now().strftime('%B/%Y')
            )

    if __name__ == '__main__':
        main()
