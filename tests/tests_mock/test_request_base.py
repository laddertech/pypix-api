"""Testes do ``_request`` e do tratamento de erro da ``BankPixAPIBase``.

Cobre o que antes não era exercitado por teste algum: o ``_handle_error_response``
real, o timeout em toda requisição e as respostas sem corpo.
"""

from typing import ClassVar
from unittest.mock import MagicMock

import pytest
import requests

from pypix_api.banks.base import BankPixAPIBase
from pypix_api.banks.exceptions import (
    PixAcessoNegadoException,
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
)
from pypix_api.http import DEFAULT_TIMEOUT
from tests.conftest import make_response


class BancoFicticio(BankPixAPIBase):
    BASE_URL = 'https://banco.exemplo/api'
    TOKEN_URL = 'https://banco.exemplo/token'
    SCOPES: ClassVar[list[str]] = ['dummy.scope']

    def get_base_url(self) -> str:
        return self.BASE_URL

    def get_bank_code(self) -> str:
        # Código real para que `_create_headers` resolva escopos de verdade
        return '748'


def cria_api(timeout=None) -> BancoFicticio:
    oauth = MagicMock()
    oauth.session = MagicMock()
    oauth.client_id = 'client-123'
    oauth.get_token.return_value = 'token-abc'
    return BancoFicticio(oauth=oauth, timeout=timeout)


# --- Timeout ------------------------------------------------------------------


def test_timeout_default_em_toda_requisicao() -> None:
    api = cria_api()
    api.session.request.return_value = make_response(200, {'ok': True})

    api.consultar_cob('txid123')

    _, kwargs = api.session.request.call_args
    assert kwargs['timeout'] == DEFAULT_TIMEOUT


def test_timeout_do_construtor_sobrepoe_o_default() -> None:
    api = cria_api(timeout=(1.0, 2.0))
    api.session.request.return_value = make_response(200, {'ok': True})

    api.consultar_cob('txid123')

    _, kwargs = api.session.request.call_args
    assert kwargs['timeout'] == (1.0, 2.0)


def test_timeout_aceita_leitura_sem_limite() -> None:
    """(conexão, None) é a forma nativa de pedir leitura sem limite."""
    api = cria_api(timeout=(5.0, None))
    assert api.timeout == (5.0, None)


def test_timeout_none_no_construtor_usa_o_default() -> None:
    """``timeout=None`` significa 'use o default', não 'espere para sempre'."""
    assert cria_api(timeout=None).timeout == DEFAULT_TIMEOUT


def test_timeout_vira_excecao_da_biblioteca() -> None:
    api = cria_api()
    api.session.request.side_effect = requests.Timeout('read timed out')

    with pytest.raises(PixTimeoutException) as exc_info:
        api.consultar_cob('txid123')

    # Falha de transporte não tem status: não houve resposta HTTP
    assert exc_info.value.status is None
    assert isinstance(exc_info.value, PixErroTransporteException)


def test_falha_de_conexao_vira_excecao_da_biblioteca() -> None:
    api = cria_api()
    api.session.request.side_effect = requests.ConnectionError('dns failure')

    with pytest.raises(PixConexaoException) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.status is None
    assert 'dns failure' in exc_info.value.detail


# --- Headers ------------------------------------------------------------------


def test_headers_de_autenticacao_sao_montados_pelo_request() -> None:
    api = cria_api()
    api.session.request.return_value = make_response(200, {'ok': True})

    api.consultar_cob('txid123')

    _, kwargs = api.session.request.call_args
    assert kwargs['headers']['Authorization'] == 'Bearer token-abc'
    assert kwargs['headers']['client_id'] == 'client-123'


def test_extra_headers_nao_derruba_a_autenticacao() -> None:
    api = cria_api()
    api.session.request.return_value = make_response(200, {'ok': True})

    api._request('GET', '/cob/x', extra_headers={'X-Correlacao': 'abc'})

    _, kwargs = api.session.request.call_args
    assert kwargs['headers']['X-Correlacao'] == 'abc'
    assert kwargs['headers']['Authorization'] == 'Bearer token-abc'


@pytest.mark.parametrize('chave', ['Authorization', 'authorization', 'client_id'])
def test_extra_headers_nao_pode_redefinir_autenticacao(chave: str) -> None:
    api = cria_api()

    with pytest.raises(ValueError, match='autenticação'):
        api._request('GET', '/cob/x', extra_headers={chave: 'invadido'})

    api.session.request.assert_not_called()
    # Erro de programação não deve custar uma requisição de token ao PSP
    api.oauth.get_token.assert_not_called()


def test_token_e_solicitado_uma_unica_vez_por_requisicao() -> None:
    """Regressão: montar headers com ``setdefault`` pedia token à toa."""
    api = cria_api()
    api.session.request.return_value = make_response(200, {'ok': True})

    api._request('GET', '/cob/x', extra_headers={'X-Correlacao': 'abc'})

    assert api.oauth.get_token.call_count == 1


# --- Respostas sem corpo ------------------------------------------------------


def test_resposta_204_sem_content_type_nao_levanta() -> None:
    """Regressão: 204 sem Content-Type levantava PixRespostaInvalidaError."""
    api = cria_api()
    api.session.request.return_value = make_response(204, content_type='')

    assert api.excluir_webhook('chave@exemplo.com') is True


@pytest.mark.parametrize('content_type', ['', 'application/json'])
def test_200_sem_corpo_onde_a_spec_exige_corpo_vira_resposta_invalida(
    content_type: str,
) -> None:
    """Quem sabe se o corpo é obrigatório é o método: `consultar_cob` precisa
    dele, e sem esta validação vazava JSONDecodeError."""
    api = cria_api()
    api.session.request.return_value = make_response(200, content_type=content_type)

    with pytest.raises(PixRespostaInvalidaError):
        api.consultar_cob('txid123')


def test_200_sem_corpo_e_valido_na_configuracao_de_webhook() -> None:
    """A especificação define `PUT /webhook/{chave}` com 200 sem corpo."""
    api = cria_api()
    api.session.request.return_value = make_response(200, content_type='')

    assert api.configurar_webhook('chave@exemplo.com', 'https://exemplo/hook') == {}


def test_202_sem_corpo_e_valido_no_lote_de_cobv() -> None:
    """A especificação define `PUT /lotecobv/{id}` com 202 sem corpo."""
    api = cria_api()
    api.session.request.return_value = make_response(202, content_type='')

    assert api.criar_lote_cobv('lote123', {'descricao': 'x', 'cobsv': []}) == {}


def test_exclusao_aceita_qualquer_2xx() -> None:
    """`_request` já levantou em caso de erro: um 200 no lugar do 204 previsto
    não pode ser lido como 'não excluiu'."""
    api = cria_api()
    api.session.request.return_value = make_response(200, content_type='')

    assert api.excluir_webhook('chave@exemplo.com') is True


# --- Mapeamento de erros ------------------------------------------------------


@pytest.mark.parametrize(
    ('status', 'tipo', 'excecao'),
    [
        (400, 'ErroValidacao', PixErroValidacaoException),
        (403, 'AcessoNegado', PixAcessoNegadoException),
        (404, 'RecursoNaoEncontrado', PixRecursoNaoEncontradoException),
        (503, 'ServicoIndisponivel', PixErroServicoIndisponivelException),
    ],
)
def test_status_de_erro_vira_excecao_tipada(status, tipo, excecao) -> None:
    api = cria_api()
    api.session.request.return_value = make_response(
        status,
        {
            'type': f'https://pix.bcb.gov.br/api/v2/error/{tipo}',
            'title': tipo,
            'status': status,
            'detail': 'detalhe do erro',
        },
    )

    with pytest.raises(excecao) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.status == status
    assert exc_info.value.detail == 'detalhe do erro'


def test_erro_sem_type_conhecido_vira_erro_desconhecido() -> None:
    api = cria_api()
    api.session.request.return_value = make_response(
        400, {'title': 'Algo', 'status': 599, 'detail': 'inesperado'}
    )

    with pytest.raises(PixErroDesconhecidoException):
        api.consultar_cob('txid123')


def test_resposta_nao_json_vira_resposta_invalida() -> None:
    api = cria_api()
    api.session.request.return_value = make_response(
        200, content=b'<html>erro</html>', content_type='text/html'
    )

    with pytest.raises(PixRespostaInvalidaError):
        api.consultar_cob('txid123')


def test_401_vira_excecao_tipada() -> None:
    api = cria_api()
    api.session.request.return_value = make_response(
        401, {'title': 'Não autorizado', 'detail': 'Cannot convert access token'}
    )

    with pytest.raises(PixNaoAutorizadoException) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.status == 401
    assert 'access token' in exc_info.value.detail


def test_500_vira_excecao_tipada_com_corpo_preservado() -> None:
    api = cria_api()
    api.session.request.return_value = make_response(
        500,
        {
            'type': 'https://pix.bcb.gov.br/api/v2/error/ErroInterno',
            'title': 'Erro interno',
            'status': 500,
            'detail': 'Condição inesperada ao processar requisição',
        },
    )

    with pytest.raises(PixErroServidorException) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.status == 500
    assert 'Condição inesperada' in exc_info.value.detail


# --- Erros sem corpo ou fora do padrão (regressão do guard de corpo vazio) ----


@pytest.mark.parametrize(
    ('status', 'excecao'),
    [
        (404, PixRecursoNaoEncontradoException),
        (500, PixErroServidorException),
        (503, PixErroServicoIndisponivelException),
    ],
)
def test_erro_sem_corpo_vira_excecao_tipada(status, excecao) -> None:
    """Regressão: erro com corpo vazio escapava do tratamento e vazava
    JSONDecodeError, porque o guard de corpo vazio valia para qualquer status."""
    api = cria_api()
    api.session.request.return_value = make_response(status, content_type='')

    with pytest.raises(excecao) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.status == status


def test_erro_sem_corpo_nao_faz_exclusao_parecer_negativa() -> None:
    """Regressão: um 500 vazio fazia excluir_webhook devolver False, como se a
    exclusão tivesse apenas não ocorrido."""
    api = cria_api()
    api.session.request.return_value = make_response(500, content_type='')

    with pytest.raises(PixErroServidorException):
        api.excluir_webhook('chave@exemplo.com')


def test_erro_com_corpo_fora_do_padrao_preserva_o_texto() -> None:
    """HTML de proxy ou texto puro: o corpo é o que o PSP pede para abrir chamado."""
    api = cria_api()
    api.session.request.return_value = make_response(
        502, content=b'<html>502 Bad Gateway</html>', content_type='text/html'
    )

    with pytest.raises(PixErroDesconhecidoException) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.status == 502
    assert 'Bad Gateway' in exc_info.value.detail


# --- Violações ----------------------------------------------------------------


def test_violacoes_do_psp_chegam_na_excecao() -> None:
    api = cria_api()
    api.session.request.return_value = make_response(
        400,
        {
            'type': 'https://pix.bcb.gov.br/api/v2/error/ErroValidacao',
            'title': 'Erro de validação',
            'status': 400,
            'detail': 'O objeto cob não respeita o schema.',
            'violacoes': [
                {'razao': 'Chave Pix não encontrada', 'propriedade': 'chave'}
            ],
        },
    )

    with pytest.raises(PixErroValidacaoException) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.violacoes == [
        {'razao': 'Chave Pix não encontrada', 'propriedade': 'chave'}
    ]
    # A razão da recusa precisa aparecer na mensagem, que é o que vai para o log
    assert 'Chave Pix não encontrada' in str(exc_info.value)


# --- Corpo de erro fora do padrão --------------------------------------------


@pytest.mark.parametrize(
    'corpo',
    [b'null', b'[{"erro": 1}]', b'"texto"', b'123'],
    ids=['null', 'lista', 'string', 'numero'],
)
def test_json_de_erro_que_nao_e_objeto_nao_vaza_excecao_crua(corpo: bytes) -> None:
    """``null`` e listas são JSON válidos: não levantam ValueError e faziam o
    acesso aos campos estourar com AttributeError."""
    api = cria_api()
    api.session.request.return_value = make_response(500, content=corpo)

    with pytest.raises(PixErroServidorException) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.status == 500
    # O corpo cru é preservado para abrir chamado
    assert exc_info.value.detail == corpo.decode()


def test_campos_nulos_no_corpo_de_erro_nao_quebram() -> None:
    api = cria_api()
    api.session.request.return_value = make_response(
        400, {'type': None, 'title': None, 'status': 400, 'detail': None}
    )

    with pytest.raises(PixErroValidacaoException) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.type == ''
    assert exc_info.value.title == 'Erro HTTP 400'
    # Sem `detail` reconhecível, o corpo cru é preservado para diagnóstico
    assert '"status": 400' in exc_info.value.detail


def test_erro_com_formato_proprio_do_gateway_preserva_o_motivo() -> None:
    """Regressão: corpo JSON com chaves fora do padrão do BACEN (formato de
    gateway) produzia exceção com detail vazio — a recusa chegava sem motivo."""
    api = cria_api()
    api.session.request.return_value = make_response(
        400, {'errors': [{'codigo': '4769515', 'mensagem': 'chave Pix inválida'}]}
    )

    with pytest.raises(PixErroValidacaoException) as exc_info:
        api.consultar_cob('txid123')

    assert 'chave Pix inválida' in exc_info.value.detail
    assert '4769515' in exc_info.value.detail


def test_corpo_cru_preserva_acentuacao_sem_charset_no_header() -> None:
    """Sem `charset` no Content-Type, `response.text` adivinha o encoding e
    erra em corpos curtos — "inválida" virava "inv√°lida" no log."""
    api = cria_api()
    api.session.request.return_value = make_response(
        500,
        content='{"msg": "não foi possível processar a transação"}'.encode(),
        content_type='application/json',
    )

    with pytest.raises(PixErroServidorException) as exc_info:
        api.consultar_cob('txid123')

    assert 'não foi possível processar a transação' in exc_info.value.detail


# --- Content-Type -------------------------------------------------------------


@pytest.mark.parametrize(
    'content_type',
    [
        'application/problem+json',
        'application/problem+json;charset=UTF-8',
        'application/json',
        'application/vnd.psp.erro+json',
    ],
)
def test_corpo_de_erro_em_qualquer_subtipo_json_e_interpretado(
    content_type: str,
) -> None:
    """A especificação do BACEN declara todo corpo de erro como
    `application/problem+json`; exigir `application/json` descartava `type`,
    `status` e `violacoes` de qualquer PSP conforme."""
    api = cria_api()
    api.session.request.return_value = make_response(
        400,
        {
            'type': 'https://pix.bcb.gov.br/api/v2/error/ErroValidacao',
            'title': 'Erro de validação',
            'status': 400,
            'detail': 'motivo real da recusa',
            'violacoes': [
                {'razao': 'Chave Pix não encontrada', 'propriedade': 'chave'}
            ],
        },
        content_type=content_type,
    )

    with pytest.raises(PixErroValidacaoException) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.detail == 'motivo real da recusa'
    assert exc_info.value.violacoes == [
        {'razao': 'Chave Pix não encontrada', 'propriedade': 'chave'}
    ]


def test_sucesso_em_problem_json_tambem_e_aceito() -> None:
    api = cria_api()
    api.session.request.return_value = make_response(
        200, {'txid': 'abc'}, content_type='application/problem+json'
    )

    assert api.consultar_cob('abc') == {'txid': 'abc'}


def test_status_como_string_no_corpo_e_respeitado() -> None:
    """O PSP pode mandar o status como string; sem coerção, o mapeamento caía
    silenciosamente em PixErroDesconhecidoException."""
    api = cria_api()
    api.session.request.return_value = make_response(
        400, {'type': '', 'status': '404', 'detail': 'não encontrado'}
    )

    with pytest.raises(PixRecursoNaoEncontradoException) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.status == 404


@pytest.mark.parametrize(
    ('violacoes', 'esperado'),
    [
        ([None], []),
        (['texto'], []),
        ([42], []),
        ([{'razao': 'ok'}, None, 'lixo'], [{'razao': 'ok'}]),
    ],
    ids=['null', 'string', 'numero', 'mista'],
)
def test_itens_de_violacoes_fora_do_formato_sao_descartados(
    violacoes, esperado
) -> None:
    """Um corpo malformado não pode derrubar a construção da exceção que o
    descreve — o AttributeError engolia o status e o detalhe do erro original."""
    api = cria_api()
    api.session.request.return_value = make_response(
        400, {'type': '', 'status': 400, 'detail': 'recusado', 'violacoes': violacoes}
    )

    with pytest.raises(PixErroValidacaoException) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.violacoes == esperado
    assert exc_info.value.detail == 'recusado'


def test_violacoes_fora_do_formato_de_lista_sao_ignoradas() -> None:
    api = cria_api()
    api.session.request.return_value = make_response(
        400, {'type': '', 'status': 400, 'violacoes': {'razao': 'objeto, não lista'}}
    )

    with pytest.raises(PixErroValidacaoException) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.violacoes == []


def test_erro_sem_violacoes_nao_quebra() -> None:
    api = cria_api()
    api.session.request.return_value = make_response(
        400, {'title': 'Erro', 'status': 400, 'detail': 'sem violações'}
    )

    with pytest.raises(PixErroValidacaoException) as exc_info:
        api.consultar_cob('txid123')

    assert exc_info.value.violacoes == []
    assert 'Violações' not in str(exc_info.value)
