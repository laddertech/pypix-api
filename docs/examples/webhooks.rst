Webhook Configuration
====================

This example shows how to configure webhooks for PIX notifications.

Setting up Webhooks
-------------------

.. code-block:: python

   from pypix_api.auth.oauth2 import OAuth2Client
   from pypix_api.banks.bb import BBPixAPI

   # Setup API
   oauth_client = OAuth2Client(
       client_id=os.getenv('BB_CLIENT_ID'),
       client_secret=os.getenv('BB_CLIENT_SECRET'),
       cert_path=os.getenv('BB_CERT_PATH'),
       cert_password=os.getenv('BB_CERT_PASSWORD'),
       scope='webhook.read webhook.write'
   )

   api = BBPixAPI(oauth=oauth_client)

Configure Webhook URL
---------------------

.. code-block:: python

   webhook_data = {
       'webhookUrl': 'https://your-domain.com/webhook/pix'
   }

   try:
       # Configure webhook for PIX charges
       result = api.criar_webhook_cob('your-pix-key', webhook_data)
       print(f"Webhook configured: {result}")

       # Configure webhook for PIX payments
       result = api.criar_webhook_pix('your-pix-key', webhook_data)
       print(f"PIX webhook configured: {result}")

   except Exception as e:
       print(f"Error configuring webhook: {e}")

Webhook Handler Example
----------------------

Here's a Flask example for handling webhook notifications:

.. code-block:: python

   from flask import Flask, request, jsonify
   import json
   import hmac
   import hashlib

   app = Flask(__name__)

   @app.route('/webhook/pix', methods=['POST'])
   def handle_pix_webhook():
       try:
           # Get webhook payload
           payload = request.get_json()

           # Verify webhook signature (if implemented)
           # signature = request.headers.get('X-Webhook-Signature')
           # if not verify_signature(request.data, signature):
           #     return jsonify({'error': 'Invalid signature'}), 401

           # Process different event types
           event_type = payload.get('event')

           if event_type == 'pix':
               handle_pix_received(payload)
           elif event_type == 'cob':
               handle_charge_updated(payload)
           else:
               print(f"Unknown event type: {event_type}")

           return jsonify({'status': 'ok'}), 200

       except Exception as e:
           print(f"Webhook error: {e}")
           return jsonify({'error': str(e)}), 500

   def handle_pix_received(payload):
       pix_data = payload.get('pix', [])
       for pix in pix_data:
           print(f"PIX received: R$ {pix.get('valor')} from {pix.get('pagador', {}).get('nome')}")
           # Process payment (update order, send confirmation, etc.)

   def handle_charge_updated(payload):
       cob_data = payload.get('cob', {})
       print(f"Charge {cob_data.get('txid')} status: {cob_data.get('status')}")
       # Process charge update

   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000)
