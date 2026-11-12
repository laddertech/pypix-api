"""Escopos do Pix Automático no Sicoob."""

from pypix_api.scopes.sicoob import SicoobScopes


def test_pix_automatico_agrega_escopos_do_spec_sicoob():
    assert SicoobScopes.PIX_AUTOMATICO.scopes == [
        'rec.write',
        'rec.read',
        'solicrec.write',
        'solicrec.read',
        'cobr.write',
        'cobr.read',
        'locr.write',
        'locr.read',
    ]


def test_pix_automatico_fica_fora_do_padrao():
    """Escopo não liberado na credencial faz o Sicoob recusar o token."""
    automatico = set(SicoobScopes.PIX_AUTOMATICO.scopes)
    assert automatico.isdisjoint(SicoobScopes.PIX.scopes)
    assert automatico.isdisjoint(SicoobScopes.TODOS_ESCOPOS.scopes)
    assert SicoobScopes.get_pix_scopes() is SicoobScopes.PIX


def test_grupos_pix_automatico_acessiveis_por_nome():
    for nome in ('pix_rec', 'pix_solicrec', 'pix_cobr', 'pix_locrec', 'pix_automatico'):
        assert SicoobScopes.get_scope_group(nome).name == nome
