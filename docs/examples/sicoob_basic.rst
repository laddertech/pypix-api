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
        token_url=SicoobPixAPI.TOKEN_URL,
        client_id=os.getenv('SICOOB_CLIENT_ID'),
        cert_pfx=os.getenv('SICOOB_CERT_PFX'),
        pwd_pfx=os.getenv('SICOOB_CERT_PASSWORD'),
    )

    # Crie a instância da API
    api = SicoobPixAPI(oauth=oauth_client)

.. note::

   Para testar no sandbox do banco, passe ``sandbox_mode=True`` **tanto** no
   ``OAuth2Client`` **quanto** no ``SicoobPixAPI`` e defina a variável de ambiente
   ``SANDBOX_TOKEN`` com o token fornecido pelo banco. Nesse modo o certificado é
   ignorado e esse token fixo é usado nas requisições (o valor padrão
   ``sandbox-token`` é apenas um placeholder e será rejeitado pela API real).

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
            token_url=SicoobPixAPI.TOKEN_URL,
            client_id=os.getenv('SICOOB_CLIENT_ID'),
            cert_pfx=os.getenv('SICOOB_CERT_PFX'),
            pwd_pfx=os.getenv('SICOOB_CERT_PASSWORD'),
        )

        api = SicoobPixAPI(oauth=oauth_client)

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
---------------------

.. code-block:: bash

    # Sicoob - Configuração
    SICOOB_CLIENT_ID=your_sicoob_client_id
    SICOOB_CERT_PFX=/path/to/sicoob/certificate.pfx
    SICOOB_CERT_PASSWORD=your_sicoob_cert_password
