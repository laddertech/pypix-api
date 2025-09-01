Sicoob - Basic Usage
===================

This example shows how to use pypix-api with Sicoob.

Setup
-----

.. code-block:: python

   from pypix_api.auth.oauth2 import OAuth2Client
   from pypix_api.banks.sicoob import SicoobPixAPI
   import os

   # Setup OAuth2 client for Sicoob
   oauth_client = OAuth2Client(
       client_id=os.getenv('SICOOB_CLIENT_ID'),
       client_secret=os.getenv('SICOOB_CLIENT_SECRET'),
       cert_path=os.getenv('SICOOB_CERT_PATH'),
       cert_password=os.getenv('SICOOB_CERT_PASSWORD'),
       scope='cob.write cob.read pix.read',
       # Sicoob specific configuration
       base_url='https://auth.sicoob.com.br'
   )

   # Create API instance
   api = SicoobPixAPI(oauth=oauth_client)

Creating a PIX Charge
---------------------

.. code-block:: python

   charge_data = {
       'calendario': {
           'expiracao': 7200  # 2 hours
       },
       'devedor': {
           'cnpj': '12345678000199',
           'nome': 'Empresa Exemplo Ltda'
       },
       'valor': {
           'original': '250.00'
       },
       'chave': 'empresa@exemplo.com.br',
       'solicitacaoPagador': 'Payment for services'
   }

   try:
       result = api.criar_cob('sicoob-txid-456', charge_data)
       print(f"Sicoob charge created: {result.get('txid')}")
   except Exception as e:
       print(f"Error: {e}")

Environment Variables for Sicoob
--------------------------------

.. code-block:: bash

   # Sicoob OAuth2 credentials
   SICOOB_CLIENT_ID=your-sicoob-client-id
   SICOOB_CLIENT_SECRET=your-sicoob-client-secret
   SICOOB_CERT_PATH=/path/to/sicoob-certificate.p12
   SICOOB_CERT_PASSWORD=sicoob-cert-password
