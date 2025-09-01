Sicoob - Exemplos Básicos
==========================

Este guia mostra como usar a pypix-api com o Sicoob para realizar operações PIX.

Configuração Inicial
--------------------

Para usar a API do Sicoob, você precisa:

1. Ter conta em cooperativa do Sistema Sicoob
2. Solicitar acesso à API PIX no seu gerente
3. Obter as credenciais de API (client_id, client_secret)
4. Baixar o certificado digital .p12

Configuração Básica
-------------------

.. code-block:: python

    import os
    from pypix_api.auth.oauth2 import OAuth2Client
    from pypix_api.banks.sicoob import SicoobPixAPI

    # Configure as credenciais
    oauth_client = OAuth2Client(
        client_id=os.getenv('SICOOB_CLIENT_ID'),
        client_secret=os.getenv('SICOOB_CLIENT_SECRET'),
        cert_path=os.getenv('SICOOB_CERT_PATH'),
        cert_password=os.getenv('SICOOB_CERT_PASSWORD'),
        scope='cob.write cob.read cobv.write cobv.read pix.read pix.write'
    )

    # Crie a instância da API
    api = SicoobPixAPI(oauth=oauth_client, sandbox_mode=True)

Criando uma Cobrança Simples
----------------------------

.. code-block:: python

    import uuid

    def criar_cobranca_sicoob():
        """Cria uma cobrança PIX no Sicoob."""

        txid = str(uuid.uuid4())

        cobranca = {
            'calendario': {
                'expiracao': 7200  # 2 horas
            },
            'devedor': {
                'cpf': '12345678901',
                'nome': 'Cliente Sicoob'
            },
            'valor': {
                'original': '150.00'
            },
            'chave': 'cooperado@sicoob.com.br',
            'solicitacaoPagador': 'Pagamento de serviços'
        }

        resultado = api.criar_cob(txid, cobranca)
        print(f"✅ Cobrança criada: {resultado['txid']}")
        return resultado

Exemplo Completo
-----------------

.. code-block:: python

    #!/usr/bin/env python3
    """Exemplo completo integração Sicoob."""

    import os
    import uuid
    from pypix_api.auth.oauth2 import OAuth2Client
    from pypix_api.banks.sicoob import SicoobPixAPI

    def main():
        """Fluxo completo com Sicoob."""

        oauth_client = OAuth2Client(
            client_id=os.getenv('SICOOB_CLIENT_ID'),
            client_secret=os.getenv('SICOOB_CLIENT_SECRET'),
            cert_path=os.getenv('SICOOB_CERT_PATH'),
            cert_password=os.getenv('SICOOB_CERT_PASSWORD'),
            scope='cob.write cob.read pix.read'
        )

        api = SicoobPixAPI(oauth=oauth_client, sandbox_mode=True)

        txid = str(uuid.uuid4())
        cobranca = {
            'calendario': {'expiracao': 3600},
            'devedor': {
                'cpf': '98765432100',
                'nome': 'Cooperado Teste'
            },
            'valor': {'original': '75.50'},
            'chave': 'cooperativa@sicoob.com.br',
            'solicitacaoPagador': 'Teste API Sicoob'
        }

        resultado = api.criar_cob(txid, cobranca)
        print(f"✅ Cobrança criada: {resultado['txid']}")

    if __name__ == '__main__':
        main()

Variáveis de Ambiente
--------------------

.. code-block:: bash

    # Sicoob - Configuração
    SICOOB_CLIENT_ID=your_sicoob_client_id
    SICOOB_CLIENT_SECRET=your_sicoob_client_secret
    SICOOB_CERT_PATH=/path/to/sicoob/certificate.p12
    SICOOB_CERT_PASSWORD=your_sicoob_cert_password
