"""
Testes para os enums de status da API Pix.

Os valores são fixados literalmente conforme a especificação do BACEN
(openapi.yaml). Qualquer divergência aqui significa que a lib passou a enviar
um status que o PSP não reconhece.
"""

import json

from pypix_api.models.enums import (
    PoliticaRetentativa,
    StatusCob,
    StatusCobR,
    StatusRec,
    StatusSolicRec,
)


def test_status_cob_valores() -> None:
    """Schema CobrancaStatus — vale para cob e cobv."""
    assert {membro.value for membro in StatusCob} == {
        'ATIVA',
        'CONCLUIDA',
        'REMOVIDA_PELO_USUARIO_RECEBEDOR',
        'REMOVIDA_PELO_PSP',
    }


def test_status_cobr_valores() -> None:
    """Schema CobRStatus."""
    assert {membro.value for membro in StatusCobR} == {
        'CRIADA',
        'ATIVA',
        'CONCLUIDA',
        'EXPIRADA',
        'REJEITADA',
        'CANCELADA',
    }


def test_status_rec_valores() -> None:
    """Schema RecStatus."""
    assert {membro.value for membro in StatusRec} == {
        'CRIADA',
        'APROVADA',
        'REJEITADA',
        'EXPIRADA',
        'CANCELADA',
    }


def test_status_solicrec_valores() -> None:
    """Schema SolicRecStatus."""
    assert {membro.value for membro in StatusSolicRec} == {
        'CRIADA',
        'ENVIADA',
        'RECEBIDA',
        'REJEITADA',
        'ACEITA',
        'EXPIRADA',
        'CANCELADA',
    }


def test_politica_retentativa_valores() -> None:
    """Schemas RecConfiguracao e CobRConfiguracao."""
    assert {membro.value for membro in PoliticaRetentativa} == {
        'NAO_PERMITE',
        'PERMITE_3R_7D',
    }


def test_status_de_cancelamento_serializa_como_string_pura() -> None:
    """O corpo do PATCH precisa sair como {"status": "CANCELADA"}."""
    for enum_status in (StatusCobR, StatusRec, StatusSolicRec):
        body = {'status': enum_status.CANCELADA.value}
        assert json.dumps(body) == '{"status": "CANCELADA"}'


def test_value_e_o_acesso_estavel_entre_versoes() -> None:
    """`.value` devolve a string da spec em qualquer versão suportada.

    `str()` devolve o nome do membro, e o resultado de f-strings mudou no
    Python 3.11 — por isso a lib usa `.value` ao montar corpos de requisição.
    """
    x = StatusCobR.CANCELADA
    assert x.value == 'CANCELADA'
    assert 'status=' + x == 'status=CANCELADA'
    assert str(x) == 'StatusCobR.CANCELADA'


def test_enums_comparam_com_string() -> None:
    """Herdar de str permite comparar direto com respostas cruas da API."""
    assert StatusCobR.CANCELADA == 'CANCELADA'
    assert (
        StatusCob.REMOVIDA_PELO_USUARIO_RECEBEDOR == 'REMOVIDA_PELO_USUARIO_RECEBEDOR'
    )
