"""Definição de escopos para a API do Banco Inter.

Os escopos são marcados por integração no Internet Banking do Inter
(Soluções para sua empresa > Nova Integração). O grupo ``PIX`` agrega o
conjunto completo (Pix comum + Pix Automático); caso a integração não possua
todos, use um subgrupo mais restrito via :meth:`get_scope_group`.

Os endpoints de simulação do sandbox não têm escopo próprio: exigem
``pix.write``, ``cobr.write`` ou ``solicrec.write``, já incluídos no grupo
``PIX``.
"""

from pypix_api.scopes.base import BankScopesBase, ScopeGroup


class InterScopes(BankScopesBase):
    """Definição de escopos para a API do Banco Inter."""

    # Informações do banco
    BANK_NAME = 'Banco Inter'
    BANK_CODE = '077'
    BANK_CODES = ['077', 'inter', 'banco_inter']

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

    # LOTECOBV - Lote de cobranças com vencimento
    LOTECOBV = ScopeGroup(
        name='lotecobv',
        scopes=['lotecobv.read', 'lotecobv.write'],
        description='Lote de cobranças com vencimento do PIX',
    )

    # PIX - Operações sobre Pix recebidos e devoluções
    PIX_BASIC = ScopeGroup(
        name='pix_basic',
        scopes=['pix.read', 'pix.write'],
        description='Consulta de Pix recebidos e devoluções',
    )

    # WEBHOOK - Webhooks do Pix comum
    WEBHOOK = ScopeGroup(
        name='webhook',
        scopes=['webhook.read', 'webhook.write'],
        description='Webhooks do PIX',
    )

    # LOCATION - Payload location (QR Code)
    LOCATION = ScopeGroup(
        name='location',
        scopes=['payloadlocation.read', 'payloadlocation.write'],
        description='Locations de payload (QR Code) do PIX',
    )

    # LOCATION_REC - Payload location de recorrência (Pix Automático)
    LOCATION_REC = ScopeGroup(
        name='location_rec',
        scopes=['payloadlocationrec.read', 'payloadlocationrec.write'],
        description='Locations de recorrência do PIX Automático',
    )

    # COBR - Cobrança recorrente (Pix Automático)
    COBR = ScopeGroup(
        name='cobr',
        scopes=['cobr.read', 'cobr.write'],
        description='Cobranças recorrentes do PIX Automático',
    )

    # REC - Recorrência (Pix Automático)
    REC = ScopeGroup(
        name='rec',
        scopes=['rec.read', 'rec.write'],
        description='Recorrências do PIX Automático',
    )

    # SOLICREC - Solicitação de recorrência (Pix Automático)
    SOLICREC = ScopeGroup(
        name='solicrec',
        scopes=['solicrec.read', 'solicrec.write'],
        description='Solicitações de recorrência do PIX Automático',
    )

    # WEBHOOK_COBR - Webhooks de cobrança recorrente
    WEBHOOK_COBR = ScopeGroup(
        name='webhook_cobr',
        scopes=['webhookcobr.read', 'webhookcobr.write'],
        description='Webhooks de cobranças recorrentes do PIX Automático',
    )

    # WEBHOOK_REC - Webhooks de recorrência
    WEBHOOK_REC = ScopeGroup(
        name='webhook_rec',
        scopes=['webhookrec.read', 'webhookrec.write'],
        description='Webhooks de recorrências do PIX Automático',
    )

    # PIX - Conjunto completo (Pix comum + Pix Automático)
    PIX = ScopeGroup(
        name='pix',
        scopes=(
            COB.scopes
            + COBV.scopes
            + LOTECOBV.scopes
            + PIX_BASIC.scopes
            + WEBHOOK.scopes
            + LOCATION.scopes
            + LOCATION_REC.scopes
            + COBR.scopes
            + REC.scopes
            + SOLICREC.scopes
            + WEBHOOK_COBR.scopes
            + WEBHOOK_REC.scopes
        ),
        description='Funcionalidades completas do PIX (comum + Automático)',
    )

    @classmethod
    def get_pix_scopes(cls) -> ScopeGroup:
        """Retorna os escopos PIX completos do Banco Inter."""
        return cls.PIX
