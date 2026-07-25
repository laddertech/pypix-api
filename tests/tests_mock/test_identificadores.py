"""
Testes para a geração de identificadores da API Pix.

A regra de formação do idRec (schema RecId) é semântica: um valor aleatório de
29 caracteres alfanuméricos passa no `pattern` do schema e mesmo assim é
recusado pelo PSP.
"""

import re
from datetime import date

import pytest

from pypix_api.models.enums import PoliticaRetentativa
from pypix_api.utils.identificadores import gerar_id_rec

# pattern do schema RecId
PATTERN_ID_REC = re.compile(r'^[a-zA-Z0-9]{29}$')

# Dígitos não-ASCII, aceitos por str.isdigit() mas fora de [0-9].
# Construídos a partir do codepoint para não inserir caracteres ambíguos no fonte.
ISPB_FULLWIDTH = ''.join(chr(0xFF10 + d) for d in range(1, 9))  # U+FF10 = '0'
ISPB_ARABE_INDICO = ''.join(chr(0x0660 + d) for d in range(1, 9))  # U+0660 = '0'


def test_formato_completo() -> None:
    """RAxxxxxxxxyyyyMMddkkkkkkkkkkk — 29 caracteres."""
    id_rec = gerar_id_rec(
        '12345678',
        PoliticaRetentativa.PERMITE_3R_7D,
        data_criacao=date(2026, 7, 25),
        sequencial='abcdefghijk',
    )
    assert id_rec == 'RR1234567820260725abcdefghijk'
    assert len(id_rec) == 29
    assert PATTERN_ID_REC.match(id_rec)


def test_prefixo_reflete_politica_de_retentativa() -> None:
    """O segundo caractere é 'R' quando permite retentativa e 'N' quando não."""
    permite = gerar_id_rec('12345678', PoliticaRetentativa.PERMITE_3R_7D)
    nao_permite = gerar_id_rec('12345678', PoliticaRetentativa.NAO_PERMITE)
    assert permite.startswith('RR')
    assert nao_permite.startswith('RN')


def test_aceita_politica_como_string() -> None:
    id_rec = gerar_id_rec('12345678', 'NAO_PERMITE')
    assert id_rec.startswith('RN')


def test_data_padrao_e_hoje() -> None:
    id_rec = gerar_id_rec('12345678', PoliticaRetentativa.PERMITE_3R_7D)
    assert id_rec[10:18] == date.today().strftime('%Y%m%d')


def test_sequencial_gerado_tem_tamanho_e_alfabeto_corretos() -> None:
    id_rec = gerar_id_rec('87654321', PoliticaRetentativa.PERMITE_3R_7D)
    sequencial = id_rec[18:]
    assert len(sequencial) == 11
    assert PATTERN_ID_REC.match(id_rec)


def test_sequencial_gerado_varia_entre_chamadas() -> None:
    gerados = {
        gerar_id_rec('12345678', PoliticaRetentativa.PERMITE_3R_7D)[18:]
        for _ in range(50)
    }
    assert len(gerados) == 50


@pytest.mark.parametrize(
    'ispb',
    [
        '1234567',  # 7 dígitos
        '123456789',  # 9 dígitos
        '1234567a',  # letra
        '',
        'abcdefgh',
        # isdigit() aceitaria estes dois, o pattern do schema não
        ISPB_FULLWIDTH,
        ISPB_ARABE_INDICO,
    ],
)
def test_ispb_invalido(ispb: str) -> None:
    with pytest.raises(ValueError, match='ispb'):
        gerar_id_rec(ispb, PoliticaRetentativa.PERMITE_3R_7D)


def test_politica_invalida() -> None:
    with pytest.raises(ValueError, match='politica_retentativa'):
        gerar_id_rec('12345678', 'PERMITE_5R_30D')


@pytest.mark.parametrize(
    'sequencial',
    [
        'abcdefghij',  # 10 caracteres
        'abcdefghijkl',  # 12 caracteres
        'abcdefghij-',  # caractere fora de [a-zA-Z0-9]
        'ábcdefghijk',  # acento: isalnum() aceitaria, o schema não
    ],
)
def test_sequencial_invalido(sequencial: str) -> None:
    with pytest.raises(ValueError, match='sequencial'):
        gerar_id_rec(
            '12345678', PoliticaRetentativa.PERMITE_3R_7D, sequencial=sequencial
        )
