Banco do Brasil - Basic Usage
=============================

This example shows how to use pypix-api with Banco do Brasil.

Setup
-----

First, configure your OAuth2 credentials:

.. code-block:: python

   from pypix_api.auth.oauth2 import OAuth2Client
   from pypix_api.banks.bb import BBPixAPI
   import os

   # Setup OAuth2 client
   oauth_client = OAuth2Client(
       client_id=os.getenv('BB_CLIENT_ID'),
       client_secret=os.getenv('BB_CLIENT_SECRET'),
       cert_path=os.getenv('BB_CERT_PATH'),
       cert_password=os.getenv('BB_CERT_PASSWORD'),
       scope='cob.write cob.read pix.read'
   )

   # Create API instance
   api = BBPixAPI(oauth=oauth_client)

Creating a PIX Charge
---------------------

.. code-block:: python

   # Define charge data
   charge_data = {
       'calendario': {
           'expiracao': 3600  # 1 hour expiration
       },
       'devedor': {
           'cpf': '12345678901',
           'nome': 'João Silva'
       },
       'valor': {
           'original': '100.50'
       },
       'chave': 'your-pix-key@example.com',
       'solicitacaoPagador': 'Payment for product X'
   }

   try:
       # Create the charge
       result = api.criar_cob('unique-txid-123', charge_data)

       print(f"Charge created successfully!")
       print(f"TxID: {result.get('txid')}")
       print(f"Status: {result.get('status')}")
       print(f"PIX Copy-Paste: {result.get('pixCopiaECola')}")
       print(f"QR Code: {result.get('qrcode')}")

   except Exception as e:
       print(f"Error creating charge: {e}")

Consulting a PIX Charge
-----------------------

.. code-block:: python

   try:
       # Get charge details
       charge = api.consultar_cob('unique-txid-123')

       print(f"Charge Status: {charge.get('status')}")
       print(f"Creation Date: {charge.get('calendario', {}).get('criacao')}")
       print(f"Expiration: {charge.get('calendario', {}).get('expiracao')}")

       # Check if payment was received
       if charge.get('status') == 'CONCLUIDA':
           pix_data = charge.get('pix', [])
           if pix_data:
               last_pix = pix_data[-1]
               print(f"Payment received: R$ {last_pix.get('valor')}")
               print(f"Payment date: {last_pix.get('horario')}")

   except Exception as e:
       print(f"Error consulting charge: {e}")

Listing PIX Charges
-------------------

.. code-block:: python

   from datetime import datetime, timedelta

   # Define date range (last 7 days)
   end_date = datetime.now()
   start_date = end_date - timedelta(days=7)

   try:
       # List charges in date range
       charges = api.consultar_lista_cob(
           inicio=start_date.isoformat() + 'Z',
           fim=end_date.isoformat() + 'Z'
       )

       print(f"Found {len(charges.get('cobs', []))} charges:")
       for cob in charges.get('cobs', []):
           print(f"- {cob.get('txid')}: {cob.get('status')} - R$ {cob.get('valor', {}).get('original', 'N/A')}")

   except Exception as e:
       print(f"Error listing charges: {e}")

Error Handling
--------------

.. code-block:: python

   from pypix_api.utils.exceptions import PixAPIError, PixAuthError

   try:
       result = api.criar_cob('txid', invalid_data)
   except PixAuthError as e:
       print(f"Authentication error: {e}")
       # Handle authentication issues (renew token, check credentials)
   except PixAPIError as e:
       print(f"API error: {e}")
       print(f"Status code: {e.status_code}")
       print(f"Response: {e.response}")
   except Exception as e:
       print(f"Unexpected error: {e}")

Environment Variables
--------------------

Create a ``.env`` file with your credentials:

.. code-block:: bash

   # Banco do Brasil OAuth2 credentials
   BB_CLIENT_ID=your-client-id-here
   BB_CLIENT_SECRET=your-client-secret-here
   BB_CERT_PATH=/path/to/your/certificate.p12
   BB_CERT_PASSWORD=your-certificate-password

   # PIX key for testing
   PIX_KEY=your-pix-key@example.com

Then load them in your Python code:

.. code-block:: python

   from dotenv import load_dotenv
   load_dotenv()

Complete Example
----------------

Here's a complete working example:

.. code-block:: python

   #!/usr/bin/env python3
   """
   Complete Banco do Brasil PIX example
   """
   import os
   from datetime import datetime
   from dotenv import load_dotenv
   from pypix_api.auth.oauth2 import OAuth2Client
   from pypix_api.banks.bb import BBPixAPI
   from pypix_api.utils.exceptions import PixAPIError, PixAuthError

   # Load environment variables
   load_dotenv()

   def main():
       # Setup
       oauth_client = OAuth2Client(
           client_id=os.getenv('BB_CLIENT_ID'),
           client_secret=os.getenv('BB_CLIENT_SECRET'),
           cert_path=os.getenv('BB_CERT_PATH'),
           cert_password=os.getenv('BB_CERT_PASSWORD'),
           scope='cob.write cob.read pix.read'
       )

       api = BBPixAPI(oauth=oauth_client)

       # Generate unique TxID
       txid = f'test-{int(datetime.now().timestamp())}'

       try:
           # Create charge
           print("Creating PIX charge...")
           charge_data = {
               'calendario': {'expiracao': 3600},
               'devedor': {
                   'cpf': '12345678901',
                   'nome': 'João Silva'
               },
               'valor': {'original': '10.00'},
               'chave': os.getenv('PIX_KEY'),
               'solicitacaoPagador': 'Test payment'
           }

           result = api.criar_cob(txid, charge_data)
           print(f"✅ Charge created: {result.get('txid')}")

           # Consult charge
           print("Consulting charge...")
           charge = api.consultar_cob(txid)
           print(f"✅ Charge status: {charge.get('status')}")

           print("PIX Copy-Paste code:")
           print(result.get('pixCopiaECola', 'Not available'))

       except PixAuthError as e:
           print(f"❌ Authentication error: {e}")
       except PixAPIError as e:
           print(f"❌ API error: {e}")
       except Exception as e:
           print(f"❌ Unexpected error: {e}")

   if __name__ == '__main__':
       main()
