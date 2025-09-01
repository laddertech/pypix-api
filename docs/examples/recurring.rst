Recurring Payments
=================

This example shows how to work with recurring PIX payments.

Creating a Recurring Payment
----------------------------

.. code-block:: python

   from pypix_api.auth.oauth2 import OAuth2Client
   from pypix_api.banks.bb import BBPixAPI
   from datetime import datetime, timedelta

   # Setup API
   oauth_client = OAuth2Client(
       client_id=os.getenv('BB_CLIENT_ID'),
       client_secret=os.getenv('BB_CLIENT_SECRET'),
       cert_path=os.getenv('BB_CERT_PATH'),
       cert_password=os.getenv('BB_CERT_PASSWORD'),
       scope='cob.write cob.read pix.read'
   )

   api = BBPixAPI(oauth=oauth_client)

   # Define recurring payment
   recurring_data = {
       'calendario': {
           'dataInicioRecorrencia': (datetime.now() + timedelta(days=1)).isoformat() + 'Z',
           'quantidade': 12,  # 12 monthly payments
           'periodicidade': 'MENSAL'
       },
       'devedor': {
           'cpf': '12345678901',
           'nome': 'João Silva'
       },
       'valor': {
           'original': '99.90'
       },
       'chave': 'subscription@example.com',
       'solicitacaoPagador': 'Monthly subscription'
   }

   try:
       result = api.criar_cobranca_recorrente('recurring-001', recurring_data)
       print(f"Recurring payment created: {result.get('txid')}")
   except Exception as e:
       print(f"Error creating recurring payment: {e}")

Managing Recurring Payments
---------------------------

.. code-block:: python

   try:
       # Consult recurring payment
       recurring = api.consultar_cobranca_recorrente('recurring-001')
       print(f"Status: {recurring.get('status')}")
       print(f"Next payment: {recurring.get('proximaCobranca')}")

       # List all recurring payments
       recurrings = api.listar_cobrancas_recorrentes()
       for rec in recurrings.get('recorrencias', []):
           print(f"ID: {rec.get('txid')}, Status: {rec.get('status')}")

   except Exception as e:
       print(f"Error managing recurring payments: {e}")

Pausing/Resuming Recurring Payments
-----------------------------------

.. code-block:: python

   try:
       # Pause recurring payment
       api.pausar_cobranca_recorrente('recurring-001')
       print("Recurring payment paused")

       # Resume recurring payment
       api.reativar_cobranca_recorrente('recurring-001')
       print("Recurring payment resumed")

   except Exception as e:
       print(f"Error managing recurring payment: {e}")

Canceling Recurring Payments
----------------------------

.. code-block:: python

   try:
       # Cancel recurring payment
       api.cancelar_cobranca_recorrente('recurring-001')
       print("Recurring payment canceled")

   except Exception as e:
       print(f"Error canceling recurring payment: {e}")
