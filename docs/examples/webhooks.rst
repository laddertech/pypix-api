Configuração de Webhooks
========================

Os webhooks permitem receber notificações em tempo real sobre eventos PIX.

Configuração Básica
-------------------

.. code-block:: python

    from pypix_api.auth.oauth2 import OAuth2Client
    from pypix_api.banks.bb import BBPixAPI

    oauth = OAuth2Client(
        token_url=BBPixAPI.TOKEN_URL,
        client_id='seu_client_id',
        cert_pfx='certificado.pfx',
        pwd_pfx='senha_cert',
    )

    api = BBPixAPI(oauth=oauth)

    def configurar_webhook():
        resultado = api.configurar_webhook(
            chave='sua-chave-pix@email.com',
            webhook_url='https://seu-sistema.com/webhook/pix',
        )
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
        # Listar webhooks existentes (por período)
        webhooks = api.listar_webhooks(
            inicio='2025-01-01T00:00:00-03:00',
            fim='2025-12-31T23:59:59-03:00',
        )
        print(f"📋 Webhooks: {len(webhooks.get('webhooks', []))}")

        # Configurar/atualizar webhook (PUT idempotente pela chave)
        resultado = api.configurar_webhook(
            chave='chave@email.com',
            webhook_url='https://novo-sistema.com/webhook',
        )

        # Consultar um webhook específico
        api.consultar_webhook(chave='chave@email.com')

        # Excluir o webhook
        api.excluir_webhook(chave='chave@email.com')

Testando Webhooks Localmente
----------------------------

Use ngrok para expor seu servidor local:

.. code-block:: bash

    # Instalar ngrok
    npm install -g ngrok

    # Expor servidor local
    ngrok http 5000

    # Use a URL gerada no webhook
