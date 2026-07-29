"""Reexporta a hierarquia de exceções, definida em :mod:`pypix_api.exceptions`.

As classes moraram aqui até a 0.10.0 e continuam importáveis deste módulo; a
definição foi movida para fora de ``banks/`` porque o ``auth/`` também a usa.
"""

from pypix_api.exceptions import (
    EXCECOES_POR_STATUS,
    PixAcessoNegadoException,
    PixAPIException,
    PixConexaoException,
    PixErroDesconhecidoException,
    PixErroServicoIndisponivelException,
    PixErroServidorException,
    PixErroTransporteException,
    PixErroValidacaoException,
    PixNaoAutorizadoException,
    PixRecursoNaoEncontradoException,
    PixRespostaInvalidaError,
    PixTimeoutException,
    excecao_para_status,
)

__all__ = [
    'EXCECOES_POR_STATUS',
    'PixAPIException',
    'PixAcessoNegadoException',
    'PixConexaoException',
    'PixErroDesconhecidoException',
    'PixErroServicoIndisponivelException',
    'PixErroServidorException',
    'PixErroTransporteException',
    'PixErroValidacaoException',
    'PixNaoAutorizadoException',
    'PixRecursoNaoEncontradoException',
    'PixRespostaInvalidaError',
    'PixTimeoutException',
    'excecao_para_status',
]
