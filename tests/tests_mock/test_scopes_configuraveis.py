"""Testes dos escopos OAuth2 configuráveis por instância.

Os escopos Pix são liberados por credencial, conforme as modalidades
contratadas junto ao PSP. Estes testes cobrem o parâmetro ``scopes`` da
``BankPixAPIBase``, o helper ``compose_scopes`` e o aviso emitido quando o PSP
concede menos escopos do que os solicitados.
"""

import logging
from typing import ClassVar
from unittest.mock import MagicMock

import pytest

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.base import BankPixAPIBase
from pypix_api.banks.sicredi import SicrediPixAPI
from pypix_api.scopes import ScopeRegistry, compose_scopes, get_pix_scopes
from pypix_api.scopes.sicredi import SicrediScopes
from tests.conftest import make_response


class BancoFicticio(BankPixAPIBase):
    BASE_URL = 'https://banco.exemplo/api'
    TOKEN_URL = 'https://banco.exemplo/token'
    SCOPES: ClassVar[list[str]] = ['dummy.scope']

    def get_base_url(self) -> str:
        return self.BASE_URL

    def get_bank_code(self) -> str:
        # Código real para que o fallback resolva escopos de verdade
        return '748'


def cria_api(**kwargs) -> BancoFicticio:  # type: ignore[no-untyped-def]
    oauth = MagicMock()
    oauth.session = MagicMock()
    oauth.client_id = 'client-123'
    oauth.get_token.return_value = 'token-abc'
    return BancoFicticio(oauth=oauth, **kwargs)


def escopo_pedido(api: BancoFicticio) -> str:
    """Executa uma chamada real e devolve o escopo que chegou ao ``get_token``."""
    api.session.request.return_value = make_response(200, {'ok': True})
    api.consultar_cob('txid123')
    api.oauth.get_token.assert_called_once()
    (escopo,), _ = api.oauth.get_token.call_args
    return escopo


# --- Formas aceitas pelo parâmetro `scopes` -----------------------------------


def test_scopes_como_string_chega_intacto() -> None:
    api = cria_api(scopes='cob.read cob.write rec.read')

    assert escopo_pedido(api) == 'cob.read cob.write rec.read'


def test_scopes_como_scope_group() -> None:
    api = cria_api(scopes=SicrediScopes.COBR)

    assert escopo_pedido(api) == 'cobr.read cobr.write'


def test_scopes_como_lista() -> None:
    api = cria_api(scopes=['cob.read', 'cob.write', 'cobr.read'])

    assert escopo_pedido(api) == 'cob.read cob.write cobr.read'


def test_scopes_como_lista_de_scope_group() -> None:
    """Combinar grupos numa lista é a forma óbvia de expressar o conjunto."""
    api = cria_api(scopes=[SicrediScopes.COB, SicrediScopes.COBR])

    assert escopo_pedido(api) == 'cob.read cob.write cobr.read cobr.write'


def test_scopes_como_lista_mista() -> None:
    api = cria_api(scopes=[SicrediScopes.COB, 'rec.read rec.write'])

    assert escopo_pedido(api) == 'cob.read cob.write rec.read rec.write'


def test_scopes_como_string_normaliza_espacos() -> None:
    api = cria_api(scopes='  cob.read   cob.write\n')

    assert escopo_pedido(api) == 'cob.read cob.write'


def test_lista_com_duplicata_deduplica_preservando_ordem() -> None:
    api = cria_api(scopes=['rec.write', 'cob.read', 'rec.write', 'cob.read'])

    assert escopo_pedido(api) == 'rec.write cob.read'


def test_scopes_explicito_nao_passa_pelo_agregado_do_banco() -> None:
    """O valor informado é enviado tal e qual, sem união com o grupo do banco."""
    api = cria_api(scopes='cob.read')

    pedido = escopo_pedido(api)

    assert pedido == 'cob.read'
    # O agregado do Sicredi tem 22 escopos; nenhum outro pode ter vazado
    assert 'cobv.read' not in pedido
    assert 'payloadlocation.read' not in pedido
    assert 'webhook.read' not in pedido


# --- Compatibilidade: `scopes=None` mantém o comportamento 0.11.0 --------------


def test_scopes_none_reproduz_grupo_completo_do_banco() -> None:
    api = cria_api()

    assert api.scopes is None
    assert escopo_pedido(api) == get_pix_scopes('748')


def test_scopes_none_e_o_padrao_da_assinatura() -> None:
    """Construir sem informar `scopes` equivale a informar `None`."""
    assert cria_api().scopes is None
    assert cria_api(scopes=None).scopes is None


def test_banco_real_aceita_scopes_sem_init_proprio() -> None:
    """Nenhum banco define `__init__`: a mudança na base propaga sozinha."""
    oauth = MagicMock()
    oauth.session = MagicMock()
    oauth.client_id = 'client-123'

    api = SicrediPixAPI(oauth=oauth, scopes=['cobr.read', 'cobr.write'])

    assert api.scopes == 'cobr.read cobr.write'


# --- Entradas malformadas -----------------------------------------------------


@pytest.mark.parametrize('valor', ['', '   ', '\n\t', [], [''], ['  ', '']])
def test_scopes_vazio_levanta_value_error(valor: str | list[str]) -> None:
    """Entrada vazia não pode virar silenciosamente 'o conjunto completo'."""
    with pytest.raises(ValueError, match='não pode ser vazio'):
        cria_api(scopes=valor)


@pytest.mark.parametrize('valor', [42, 3.5, {'cob': 'read'}.keys, object()])
def test_scopes_de_tipo_invalido_levanta_type_error(valor: object) -> None:
    """O erro precisa nomear `scopes`, e não vazar um AttributeError de split."""
    with pytest.raises(TypeError, match='`scopes` aceita str, ScopeGroup'):
        cria_api(scopes=valor)


@pytest.mark.parametrize('item', [None, 42, ['cob.read']])
def test_item_de_tipo_invalido_na_lista_levanta_type_error(item: object) -> None:
    with pytest.raises(TypeError, match='`scopes` aceita str, ScopeGroup'):
        cria_api(scopes=['cob.read', item])


# --- compose_scopes -----------------------------------------------------------


def test_compose_scopes_pix_automatico_sicredi() -> None:
    scopes = compose_scopes(
        '748', 'cob', 'cobr', 'rec', 'solicrec', 'webhook_rec', 'webhook_cobr'
    )

    assert scopes == (
        'cob.read cob.write '
        'cobr.read cobr.write '
        'rec.read rec.write '
        'solicrec.read solicrec.write '
        'webhookrec.read webhookrec.write '
        'webhookcobr.read webhookcobr.write'
    )
    # As modalidades não contratadas ficam de fora
    for ausente in ('cobv.', 'lotecobv.', 'payloadlocation.', 'webhook.'):
        assert ausente not in scopes


def test_compose_scopes_delega_ao_registry() -> None:
    assert compose_scopes('748', 'cob', 'rec') == ScopeRegistry.combine_scopes(
        '748', 'cob', 'rec'
    )


def test_compose_scopes_deduplica_grupos_repetidos() -> None:
    assert compose_scopes('748', 'cob', 'cob') == 'cob.read cob.write'


def test_compose_scopes_aceita_alias_do_banco() -> None:
    assert compose_scopes('sicredi', 'cobr') == compose_scopes('748', 'cobr')


def test_compose_scopes_banco_desconhecido() -> None:
    with pytest.raises(ValueError, match='não encontrado'):
        compose_scopes('999', 'cob')


def test_compose_scopes_grupo_inexistente_lista_os_disponiveis() -> None:
    """O grupo é WEBHOOK_REC, mas o escopo é webhookrec.read — confusão provável."""
    with pytest.raises(ValueError) as exc:
        compose_scopes('748', 'cob', 'webhookrec')

    mensagem = str(exc.value)
    invalidos, disponiveis = mensagem.split('Disponíveis:')
    assert 'webhookrec' in invalidos  # o grupo errado é nomeado
    assert 'cob' not in invalidos  # o grupo válido não é acusado
    assert 'WEBHOOK_REC' in disponiveis  # o nome correto aparece na lista


def test_compose_scopes_alimenta_o_parametro_scopes() -> None:
    """Uso alvo documentado: compose_scopes -> scopes=."""
    scopes = compose_scopes('748', 'cob', 'cobr', 'rec', 'solicrec')
    api = cria_api(scopes=scopes)

    assert escopo_pedido(api) == scopes


# --- Diagnóstico do escopo concedido pelo PSP ---------------------------------


def cria_oauth_com_resposta(corpo: dict) -> tuple[OAuth2Client, list]:  # type: ignore[type-arg]
    client = OAuth2Client(
        token_url='https://api-pix.sicredi.com.br/oauth/token',
        client_id='id',
        client_secret='secret',
        sandbox_mode=True,
    )
    chamadas: list = []

    def fake_post(url, data=None, headers=None, timeout=None):  # type: ignore[no-untyped-def]
        chamadas.append(data)
        return make_response(200, corpo)

    client.session.post = fake_post  # type: ignore[method-assign]
    return client, chamadas


def test_avisa_quando_psp_concede_menos_escopos(
    caplog: pytest.LogCaptureFixture,
) -> None:
    client, _ = cria_oauth_com_resposta(
        {
            'access_token': 'abc',
            'expires_in': 3600,
            # O PSP devolve só o que a credencial tem contratado
            'scope': 'cob.read cob.write',
        }
    )

    with caplog.at_level(logging.WARNING, logger='pypix_api.auth.oauth2'):
        assert client.get_token('cob.read cob.write cobr.read cobr.write') == 'abc'

    assert len(caplog.records) == 1
    registro = caplog.records[0]
    assert registro.levelno == logging.WARNING
    mensagem = registro.getMessage()
    assert 'cobr.read cobr.write' in mensagem
    assert 'cob.read' in mensagem


def test_aviso_limita_o_tamanho_da_lista_de_escopos(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """O campo `scope` vem do PSP e não tem limite; a linha de log tem."""
    solicitados = ' '.join(f'escopo{i}' for i in range(50))
    client, _ = cria_oauth_com_resposta(
        {'access_token': 'abc', 'expires_in': 3600, 'scope': 'outro'}
    )

    with caplog.at_level(logging.WARNING, logger='pypix_api.auth.oauth2'):
        client.get_token(solicitados)

    mensagem = caplog.records[0].getMessage()
    assert 'escopo0 ' in mensagem
    assert '(+30)' in mensagem  # 50 ausentes, 20 listados
    assert 'escopo49' not in mensagem
    assert len(mensagem) < 500


def test_nao_avisa_quando_escopo_concedido_e_o_solicitado(
    caplog: pytest.LogCaptureFixture,
) -> None:
    client, _ = cria_oauth_com_resposta(
        {'access_token': 'abc', 'expires_in': 3600, 'scope': 'cob.write cob.read'}
    )

    with caplog.at_level(logging.WARNING, logger='pypix_api.auth.oauth2'):
        client.get_token('cob.read cob.write')

    assert caplog.records == []


def test_nao_avisa_quando_resposta_omite_o_campo_scope(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A RFC 6749 torna `scope` opcional quando é idêntico ao solicitado."""
    client, _ = cria_oauth_com_resposta({'access_token': 'abc', 'expires_in': 3600})

    with caplog.at_level(logging.WARNING, logger='pypix_api.auth.oauth2'):
        client.get_token('cob.read cob.write')

    assert caplog.records == []


def test_aviso_nao_bloqueia_a_obtencao_do_token() -> None:
    """O escopo negado é diagnóstico: o token válido continua sendo devolvido."""
    client, _ = cria_oauth_com_resposta(
        {'access_token': 'abc', 'expires_in': 3600, 'scope': ''}
    )

    assert client.get_token('cob.read') == 'abc'


# --- Cache de token por conjunto de escopos -----------------------------------


def test_cache_reaproveita_token_quando_muda_so_a_ordem() -> None:
    """Mesmo conjunto, ordem diferente: um POST /oauth/token, não dois.

    O Guia Técnico do Sicredi (§11) associa volume de requisições de token a
    bloqueio por IP — e com escopos configuráveis a mesma combinação passa a ser
    montada em pontos diferentes da aplicação.
    """
    client, chamadas = cria_oauth_com_resposta(
        {'access_token': 'abc', 'expires_in': 3600}
    )

    client.get_token('cob.read cob.write')
    client.get_token('cob.write cob.read')
    client.get_token('cob.read cob.write cob.read')

    assert len(chamadas) == 1
    assert list(client.token_cache) == ['cob.read cob.write']


def test_cache_separa_conjuntos_diferentes() -> None:
    client, chamadas = cria_oauth_com_resposta(
        {'access_token': 'abc', 'expires_in': 3600}
    )

    client.get_token('cob.read')
    client.get_token('cob.read cobr.read')

    assert len(chamadas) == 2


def test_ordem_original_e_preservada_no_envio_ao_psp() -> None:
    """A canonização é só da chave do cache; o PSP recebe o que foi pedido."""
    client, chamadas = cria_oauth_com_resposta(
        {'access_token': 'abc', 'expires_in': 3600}
    )

    client.get_token('webhookrec.write cob.read')

    assert chamadas[0]['scope'] == 'webhookrec.write cob.read'
