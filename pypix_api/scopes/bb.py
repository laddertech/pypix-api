"""Definição de escopos para a API do Banco do Brasil."""

from pypix_api.scopes.base import BankScopesBase, ScopeGroup


class BBScopes(BankScopesBase):
    """Definição de escopos para a API do Banco do Brasil."""

    # Informações do banco
    BANK_NAME = 'Banco do Brasil'
    BANK_CODE = '001'
    BANK_CODES = ['001', 'bb', 'banco_do_brasil']

    # PIX - Funcionalidades relacionadas ao PIX
    PIX = ScopeGroup(
        name='pix',
        scopes=['pix.read', 'pix.write'],
        description='Funcionalidades do PIX do Banco do Brasil',
    )

    # COB - Cobrança imediata
    COB = ScopeGroup(
        name='cob',
        scopes=['cob.read', 'cob.write'],
        description='Cobranças imediatas do PIX',
    )

    # COBV - Cobrança com vencimento
    COBV = ScopeGroup(
        name='cobv',
        scopes=['cobv.read', 'cobv.write'],
        description='Cobranças com vencimento do PIX',
    )

    # COBR - Cobrança recorrente
    COBR = ScopeGroup(
        name='cobr',
        scopes=['cobr.read', 'cobr.write'],
        description='Cobranças recorrentes do PIX',
    )

    # LOTECOBV - Lote de cobranças com vencimento
    LOTECOBV = ScopeGroup(
        name='lotecobv',
        scopes=['lotecobv.read', 'lotecobv.write'],
        description='Lote de cobranças com vencimento do PIX',
    )

    # REC - Recorrência
    REC = ScopeGroup(
        name='rec',
        scopes=['rec.read', 'rec.write'],
        description='Recorrências do PIX',
    )

    # SOLICREC - Solicitação de recorrência
    SOLICREC = ScopeGroup(
        name='solicrec',
        scopes=['solicrec.read', 'solicrec.write'],
        description='Solicitações de recorrência do PIX',
    )

    # LOCATION - Payload location (QR Code)
    LOCATION = ScopeGroup(
        name='location',
        scopes=['payloadlocation.read', 'payloadlocation.write'],
        description='Locations de payload (QR Code) do PIX',
    )

    # WEBHOOK - Webhooks gerais
    WEBHOOK = ScopeGroup(
        name='webhook',
        scopes=['webhook.read', 'webhook.write'],
        description='Webhooks do PIX',
    )

    # WEBHOOK_COBR - Webhooks de cobrança recorrente
    WEBHOOK_COBR = ScopeGroup(
        name='webhook_cobr',
        scopes=['webhookcobr.read', 'webhookcobr.write'],
        description='Webhooks de cobranças recorrentes do PIX',
    )

    # WEBHOOK_REC - Webhooks de recorrência
    WEBHOOK_REC = ScopeGroup(
        name='webhook_rec',
        scopes=['webhookrec.read', 'webhookrec.write'],
        description='Webhooks de recorrências do PIX',
    )

    # Conta Corrente - Funcionalidades de conta corrente
    CONTA_CORRENTE = ScopeGroup(
        name='conta_corrente',
        scopes=['cco_extrato', 'cco_consulta'],
        description='Funcionalidades de conta corrente',
    )

    # Boleto - Funcionalidades de boleto bancário
    BOLETO = ScopeGroup(
        name='boleto',
        scopes=[
            'boletos_inclusao',
            'boletos_consulta',
            'boletos_alteracao',
            'webhooks_alteracao',
            'webhooks_consulta',
            'webhooks_inclusao',
        ],
        description='Funcionalidades de boleto bancário',
    )

    @classmethod
    def get_pix_scopes(cls) -> ScopeGroup:
        """Retorna os escopos PIX do Banco do Brasil."""
        return cls.PIX
