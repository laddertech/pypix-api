"""pypix-api: Biblioteca Python para integracao com APIs bancarias do PIX.

Esta biblioteca facilita a integracao com APIs de bancos brasileiros,
fornecendo uma interface simples e consistente para operacoes PIX.
"""

__version__ = '0.5.0'
__author__ = 'Fabio Thomaz'
__email__ = 'fabio@ladder.dev.br'
__license__ = 'MIT'

# Exports principais
from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.bb import BBPixAPI
from pypix_api.banks.sicoob import SicoobPixAPI
from pypix_api.models.pix import PixCobranca

__all__ = [
    'BBPixAPI',
    'OAuth2Client',
    'PixCobranca',
    'SicoobPixAPI',
    '__author__',
    '__email__',
    '__license__',
    '__version__',
]
