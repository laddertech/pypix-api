Sicredi - Exemplos Básicos
===========================

Este guia mostra como usar a pypix-api com o Sicredi para realizar operações PIX.

Configuração Inicial
--------------------

Para usar a API do Sicredi, você precisa:

1. Ter conta em cooperativa do Sistema Sicredi
2. Solicitar acesso à API PIX no seu gerente/canal de desenvolvedores
3. Obter as credenciais de API (``client_id`` e ``client_secret``)
4. Baixar o certificado digital (.pfx/.p12)

.. note::

   O Sicredi difere do BB e do Sicoob em dois pontos:

   - **Autenticação HTTP Basic**: o token é solicitado com
     ``Authorization: Basic base64(client_id:client_secret)``, então o
     ``client_secret`` é **obrigatório** no ``OAuth2Client``.
   - **Versionamento por recurso**: a ``BASE_URL`` aponta para a raiz ``/api`` e a
     versão de cada endpoint (``v1``/``v2``/``v3``) é resolvida internamente pela
     ``SicrediPixAPI``.

Configuração Básica
-------------------

.. code-block:: python

    import os
    from pypix_api.auth.oauth2 import OAuth2Client
    from pypix_api.banks.sicredi import SicrediPixAPI

    # Configure as credenciais (client_secret é obrigatório no Sicredi)
    oauth_client = OAuth2Client(
        token_url=SicrediPixAPI.TOKEN_URL,
        client_id=os.getenv('SICREDI_CLIENT_ID'),
        client_secret=os.getenv('SICREDI_CLIENT_SECRET'),
        cert_pfx=os.getenv('SICREDI_CERT_PFX'),
        pwd_pfx=os.getenv('SICREDI_CERT_PASSWORD'),
    )

    # Crie a instância da API
    api = SicrediPixAPI(oauth=oauth_client)

.. note::

   Para testar no ambiente de homologação do Sicredi, use
   ``token_url=SicrediPixAPI.SANDBOX_TOKEN_URL`` (que aponta para a raiz de
   homologação) mantendo o certificado — o fluxo real de homologação usa mTLS, e
   **não** o ``sandbox_mode`` (token fixo) da biblioteca.

Criando uma Cobrança Simples
----------------------------

.. code-block:: python

    import uuid

    def criar_cobranca_sicredi():
        """Cria uma cobrança PIX imediata no Sicredi."""

        txid = str(uuid.uuid4())

        cobranca = {
            'calendario': {
                'expiracao': 3600
            },
            'devedor': {
                'cpf': '12345678909',
                'nome': 'Francisco da Silva'
            },
            'valor': {
                'original': '37.00'
            },
            'chave': '5f84a4c5-c5cb-4599-9f13-7eb4d419dacc',
            'solicitacaoPagador': 'Pagamento de serviços.'
        }

        resultado = api.criar_cob(txid, cobranca)
        print(f"✅ Cobrança criada: {resultado['txid']}")
        return resultado

Exemplo Completo
-----------------

.. code-block:: python

    #!/usr/bin/env python3
    """Exemplo completo integração Sicredi."""

    import os
    import uuid
    from pypix_api.auth.oauth2 import OAuth2Client
    from pypix_api.banks.sicredi import SicrediPixAPI

    def main():
        """Fluxo completo com Sicredi."""

        oauth_client = OAuth2Client(
            token_url=SicrediPixAPI.TOKEN_URL,
            client_id=os.getenv('SICREDI_CLIENT_ID'),
            client_secret=os.getenv('SICREDI_CLIENT_SECRET'),
            cert_pfx=os.getenv('SICREDI_CERT_PFX'),
            pwd_pfx=os.getenv('SICREDI_CERT_PASSWORD'),
        )

        api = SicrediPixAPI(oauth=oauth_client)

        txid = str(uuid.uuid4())
        cobranca = {
            'calendario': {'expiracao': 3600},
            'devedor': {
                'cpf': '12345678909',
                'nome': 'Cooperado Teste'
            },
            'valor': {'original': '75.50'},
            'chave': '5f84a4c5-c5cb-4599-9f13-7eb4d419dacc',
            'solicitacaoPagador': 'Teste API Sicredi'
        }

        resultado = api.criar_cob(txid, cobranca)
        print(f"✅ Cobrança criada: {resultado['txid']}")

    if __name__ == '__main__':
        main()

Variáveis de Ambiente
---------------------

.. code-block:: bash

    # Sicredi - Configuração
    SICREDI_CLIENT_ID=your_sicredi_client_id
    SICREDI_CLIENT_SECRET=your_sicredi_client_secret
    SICREDI_CERT_PFX=/path/to/sicredi/certificate.pfx
    SICREDI_CERT_PASSWORD=your_sicredi_cert_password
