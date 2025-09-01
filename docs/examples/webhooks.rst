Configuração de Webhooks
========================

Os webhooks permitem receber notificações em tempo real sobre eventos PIX.

Configuração Básica
-------------------

.. code-block:: python

    from pypix_api.auth.oauth2 import OAuth2Client
    from pypix_api.banks.bb import BBPixAPI

    oauth = OAuth2Client(
        client_id='seu_client_id',
        client_secret='seu_client_secret',
        cert_path='certificado.p12',
        cert_password='senha_cert',
        scope='webhook.read webhook.write'
    )

    api = BBPixAPI(oauth=oauth)

    def configurar_webhook():
        webhook_config = {
            'webhookUrl': 'https://seu-sistema.com/webhook/pix',
            'chave': 'sua-chave-pix@email.com'
        }

        resultado = api.criar_webhook('pix', webhook_config)
        print(f"✅ Webhook configurado: {resultado['webhookUrl']}")

Servidor Flask para Webhooks
----------------------------

.. code-block:: python

    from flask import Flask, request, jsonify

    app = Flask(__name__)

    @app.route('/webhook/pix', methods=['POST'])
    def webhook_pix():
        try:
            data = request.get_json()

            if data.get('tipo') == 'cobranca':
                processar_cobranca(data.get('cobranca', {}))
            elif data.get('tipo') == 'pix':
                processar_pix_recebido(data.get('pix', {}))

            return jsonify({'status': 'ok'}), 200

        except Exception as e:
            return jsonify({'erro': str(e)}), 500

    def processar_cobranca(cobranca):
        txid = cobranca.get('txid')
        status = cobranca.get('status')

        if status == 'CONCLUIDA':
            print(f"✅ Pagamento recebido: {txid}")

    def processar_pix_recebido(pix):
        e2e_id = pix.get('endToEndId')
        valor = pix.get('valor')
        print(f"💰 PIX recebido: R$ {valor} ({e2e_id})")

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)

Gerenciamento de Webhooks
-------------------------

.. code-block:: python

    def gerenciar_webhooks():
        # Listar webhooks existentes
        webhooks = api.consultar_webhooks('pix')
        print(f"📋 Webhooks: {len(webhooks.get('webhooks', []))}")

        # Configurar novo webhook
        resultado = api.criar_webhook('pix', {
            'webhookUrl': 'https://novo-sistema.com/webhook',
            'chave': 'chave@email.com'
        })

        # Atualizar webhook
        api.atualizar_webhook('pix', 'chave@email.com', {
            'webhookUrl': 'https://sistema-atualizado.com/webhook'
        })

Testando Webhooks Localmente
----------------------------

Use ngrok para expor seu servidor local:

.. code-block:: bash

    # Instalar ngrok
    npm install -g ngrok

    # Expor servidor local
    ngrok http 5000

    # Use a URL gerada no webhook
