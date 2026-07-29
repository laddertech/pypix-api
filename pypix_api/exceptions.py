"""Hierarquia de exceções da biblioteca.

Toda falha levantada pelo `pypix_api` — erro devolvido pelo PSP, resposta fora
do contrato ou falha de transporte — herda de :class:`PixAPIException`, de modo
que um único ``except`` cobre o caminho inteiro, incluindo a requisição de
token.

Mora fora de ``banks/`` porque também é usada pelo ``auth/``; o módulo
``pypix_api.banks.exceptions`` reexporta tudo para não quebrar imports
existentes.
"""

from typing import Any


class PixAPIException(Exception):
    """Exceção base para erros da API Pix.

    Args:
        type_: URI do tipo de erro devolvida pelo PSP
        title: Título do erro
        status: Código HTTP da resposta. ``None`` quando a falha ocorreu antes
            de haver resposta (timeout, erro de conexão)
        detail: Descrição detalhada do erro
        violacoes: Lista de violações devolvida pelo PSP, quando houver. É onde
            o PSP informa o motivo real de um 400. Itens fora do formato de
            objeto são descartados — um corpo malformado não pode derrubar a
            construção da própria exceção que o descreve
    """

    def __init__(
        self,
        type_: str = '',
        title: str = '',
        status: int | None = None,
        detail: str = '',
        violacoes: list[dict[str, Any]] | None = None,
    ):
        self.type = type_
        self.title = title
        self.status = status
        self.detail = detail
        self.violacoes = self._normaliza_violacoes(violacoes)
        super().__init__(self._build_message())

    @staticmethod
    def _normaliza_violacoes(violacoes: Any) -> list[dict[str, Any]]:
        if not isinstance(violacoes, list):
            return []
        return [item for item in violacoes if isinstance(item, dict)]

    def _build_message(self) -> str:
        mensagem = f'{self.title} ({self.status}): {self.detail} [{self.type}]'
        if self.violacoes:
            detalhes = '; '.join(
                f'{v.get("propriedade", "?")}: {v.get("razao", "?")}'
                for v in self.violacoes
            )
            mensagem = f'{mensagem} Violações: {detalhes}'
        return mensagem


class PixAcessoNegadoException(PixAPIException):
    """Erro de acesso negado (403)."""


class PixRecursoNaoEncontradoException(PixAPIException):
    """Erro de recurso não encontrado (404)."""


class PixErroValidacaoException(PixAPIException):
    """Erro de validação (400)."""


class PixNaoAutorizadoException(PixAPIException):
    """Erro de autenticação (401).

    Token ausente, expirado ou alterado entre o recebimento e o envio; ou
    credencial recusada pelo endpoint de token.
    """


class PixErroServicoIndisponivelException(PixAPIException):
    """Erro de serviço indisponível (503)."""


class PixErroServidorException(PixAPIException):
    """Erro interno do PSP (500).

    O corpo da resposta é preservado em ``detail``: os PSPs costumam pedi-lo
    para abrir chamado.
    """


class PixErroDesconhecidoException(PixAPIException):
    """Erro desconhecido da API Pix."""


class PixRespostaInvalidaError(PixAPIException):
    """Erro quando a resposta da API não está no formato esperado"""


class PixErroTransporteException(PixAPIException):
    """Falha ocorrida antes de haver resposta HTTP.

    Não possui ``status``: a requisição não chegou a ser respondida pelo PSP.
    """

    def __init__(self, detail: str = '', title: str = 'Erro de transporte'):
        super().__init__(type_='', title=title, status=None, detail=detail)


class PixTimeoutException(PixErroTransporteException):
    """A requisição excedeu o tempo limite.

    O resultado da operação é **desconhecido**: o PSP pode tê-la processado e
    apenas a resposta ter se perdido. Consulte o recurso antes de recriá-lo em
    operações que geram identificador no PSP (``POST /cob``, ``/cobr``, ``/rec``,
    ``/solicrec``, ``/loc``, ``/locrec``).
    """

    def __init__(self, detail: str = ''):
        super().__init__(detail=detail, title='Tempo limite excedido')


class PixConexaoException(PixErroTransporteException):
    """Falha de conexão com o PSP (DNS, TLS, rede)."""

    def __init__(self, detail: str = ''):
        super().__init__(detail=detail, title='Falha de conexão')


#: Exceção correspondente a cada status HTTP de erro.
EXCECOES_POR_STATUS: dict[int, type[PixAPIException]] = {
    400: PixErroValidacaoException,
    401: PixNaoAutorizadoException,
    403: PixAcessoNegadoException,
    404: PixRecursoNaoEncontradoException,
    500: PixErroServidorException,
    503: PixErroServicoIndisponivelException,
}


def excecao_para_status(status: int) -> type[PixAPIException]:
    """Resolve a exceção de um status HTTP de erro."""
    return EXCECOES_POR_STATUS.get(status, PixErroDesconhecidoException)
