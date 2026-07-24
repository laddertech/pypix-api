Banco do Brasil - Exemplos Básicos
===================================

Este guia mostra como usar a pypix-api com o Banco do Brasil para realizar operações PIX.

Configuração Inicial
--------------------

Primeiro, você precisa obter suas credenciais do Banco do Brasil no Portal do Desenvolvedor:

1. Acesse o `Portal do Desenvolvedor BB <https://developers.bb.com.br/>`_
2. Crie uma aplicação PIX
3. Baixe o certificado .p12
4. Obtenha seu client_id e client_secret

Configuração Básica
-------------------

.. code-block:: python

    import os
    from pypix_api.auth.oauth2 import OAuth2Client
    from pypix_api.banks.bb import BBPixAPI

    # Configure as credenciais (prefira usar variáveis de ambiente)
    oauth_client = OAuth2Client(
        token_url=BBPixAPI.TOKEN_URL,
        client_id=os.getenv('BB_CLIENT_ID'),
        cert_pfx=os.getenv('BB_CERT_PFX'),  # Caminho para o arquivo .pfx/.p12
        pwd_pfx=os.getenv('BB_CERT_PASSWORD'),
    )

    # Crie a instância da API
    api = BBPixAPI(oauth=oauth_client)

.. note::

   Para testar no sandbox do banco, passe ``sandbox_mode=True`` **tanto** no
   ``OAuth2Client`` **quanto** no ``BBPixAPI`` e defina a variável de ambiente
   ``SANDBOX_TOKEN`` com o token fornecido pelo banco. Nesse modo o certificado é
   ignorado e esse token fixo é usado nas requisições (o valor padrão
   ``sandbox-token`` é apenas um placeholder e será rejeitado pela API real).

Criando uma Cobrança Imediata
-----------------------------

.. code-block:: python

    from decimal import Decimal
    import uuid

    def criar_cobranca_simples():
        """Cria uma cobrança PIX imediata simples."""

        # Gera um txid único (obrigatório)
        txid = str(uuid.uuid4())

        # Dados da cobrança
        cobranca = {
            'calendario': {
                'expiracao': 3600  # Expira em 1 hora
            },
            'devedor': {
                'cpf': '12345678901',  # CPF do pagador
                'nome': 'João da Silva'
            },
            'valor': {
                'original': '99.90'  # Valor em string
            },
            'chave': 'sua-chave-pix@email.com',  # Sua chave PIX
            'solicitacaoPagador': 'Pagamento de produtos da loja online'
        }

        try:
            # Cria a cobrança
            resultado = api.criar_cob(txid, cobranca)

            print(f"✅ Cobrança criada com sucesso!")
            print(f"TxID: {resultado['txid']}")
            print(f"Status: {resultado['status']}")
            print(f"QR Code: {resultado['pixCopiaECola']}")

            return resultado

        except Exception as e:
            print(f"❌ Erro ao criar cobrança: {e}")
            return None

Exemplo Completo
----------------

.. code-block:: python

    #!/usr/bin/env python3
    """Exemplo completo de uso da pypix-api com Banco do Brasil."""

    import os
    import uuid
    from datetime import datetime, timedelta
    from pypix_api.auth.oauth2 import OAuth2Client
    from pypix_api.banks.bb import BBPixAPI

    def main():
        """Exemplo principal que demonstra o fluxo completo."""

        # Configuração
        oauth_client = OAuth2Client(
            token_url=BBPixAPI.TOKEN_URL,
            client_id=os.getenv('BB_CLIENT_ID'),
            cert_pfx=os.getenv('BB_CERT_PFX'),
            pwd_pfx=os.getenv('BB_CERT_PASSWORD'),
        )

        api = BBPixAPI(oauth=oauth_client)

        print("🏦 Conectando ao Banco do Brasil...")

        # 1. Criar uma cobrança
        txid = str(uuid.uuid4())
        cobranca = {
            'calendario': {'expiracao': 3600},
            'devedor': {
                'cpf': '12345678901',
                'nome': 'Cliente Teste'
            },
            'valor': {'original': '50.00'},
            'chave': 'sua-chave@email.com',
            'solicitacaoPagador': 'Teste de cobrança'
        }

        resultado = api.criar_cob(txid, cobranca)
        print(f"✅ Cobrança criada: {resultado['txid']}")

    if __name__ == '__main__':
        main()

Variáveis de Ambiente
---------------------

Crie um arquivo ``.env`` na raiz do seu projeto:

.. code-block:: bash

    # Banco do Brasil - Produção
    BB_CLIENT_ID=your_production_client_id
    BB_CERT_PFX=/path/to/production/certificate.pfx
    BB_CERT_PASSWORD=your_certificate_password
