"""Módulo de escopos bancários."""

from pypix_api.scopes.base import ScopeGroup
from pypix_api.scopes.bb import BBScopes
from pypix_api.scopes.registry import ScopeRegistry, get_bank_scopes, get_pix_scopes
from pypix_api.scopes.sicoob import SicoobScopes
from pypix_api.scopes.sicredi import SicrediScopes

# Registrar todos os bancos
ScopeRegistry.register('756', SicoobScopes)
ScopeRegistry.register('sicoob', SicoobScopes)

ScopeRegistry.register('001', BBScopes)
ScopeRegistry.register('bb', BBScopes)
ScopeRegistry.register('banco_do_brasil', BBScopes)

ScopeRegistry.register('748', SicrediScopes)
ScopeRegistry.register('sicredi', SicrediScopes)


def compose_scopes(bank_code: str, *group_names: str) -> str:
    """Compõe os escopos de um banco a partir dos nomes dos grupos desejados.

    Os escopos Pix são liberados **por credencial**, conforme as modalidades
    que o associado contratou com o PSP. Pedir o grupo Pix completo do banco
    quando só algumas modalidades foram contratadas viola o menor privilégio e,
    dependendo do PSP, resulta em recusa do token ou em concessão silenciosa de
    um subconjunto. Use esta função para pedir exatamente o que a credencial
    tem, e informe o resultado em ``scopes=`` ao construir o cliente do banco::

        from pypix_api.banks.sicredi import SicrediPixAPI
        from pypix_api.scopes import compose_scopes

        scopes = compose_scopes(
            '748', 'cob', 'cobr', 'rec', 'solicrec', 'webhook_rec', 'webhook_cobr'
        )
        api = SicrediPixAPI(oauth=oauth, scopes=scopes)

    Os grupos disponíveis de um banco podem ser listados com
    :meth:`ScopeRegistry.list_scope_groups`.

    Args:
        bank_code: Código do banco (ex.: ``'748'``, ``'sicredi'``)
        *group_names: Nomes dos grupos de escopos, sem distinção de caixa
            (ex.: ``'cob'``, ``'webhook_rec'``)

    Returns:
        str: Escopos combinados, separados por espaço, sem duplicatas e na
        ordem em que os grupos foram informados

    Raises:
        ValueError: Se o banco não estiver registrado, ou se algum grupo não
            existir no banco — a mensagem lista os grupos disponíveis
    """
    # Os nomes são conferidos antes de compor: o `getattr` do registry falharia
    # com um `AttributeError` que não diz quais grupos existem, e a confusão é
    # provável — o escopo se chama `webhookrec.read`, mas o grupo, WEBHOOK_REC.
    disponiveis = ScopeRegistry.list_scope_groups(bank_code)
    conhecidos = {nome.upper() for nome in disponiveis}
    invalidos = [nome for nome in group_names if nome.upper() not in conhecidos]
    if invalidos:
        raise ValueError(
            f'Grupo(s) de escopos inexistente(s) no banco {bank_code!r}: '
            f'{", ".join(invalidos)}. Disponíveis: {", ".join(disponiveis)}'
        )

    return ScopeRegistry.combine_scopes(bank_code, *group_names)


# Exportar funções principais
__all__ = [
    'BBScopes',
    'ScopeGroup',
    'ScopeRegistry',
    'SicoobScopes',
    'SicrediScopes',
    'compose_scopes',
    'get_bank_scopes',
    'get_pix_scopes',
]
