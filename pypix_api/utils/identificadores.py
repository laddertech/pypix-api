"""
pypix_api.utils.identificadores
-------------------------------

Geração de identificadores da API Pix que possuem regra de formação semântica.

O ``idRec`` do Pix Automático não é um identificador livre: além de ter 29
caracteres alfanuméricos, ele codifica no próprio valor a política de
retentativa, o ISPB do participante e a data de criação. Um valor aleatório
passa na validação de formato do schema (``pattern: [a-zA-Z0-9]{29}``) e mesmo
assim é recusado pelo PSP — daí a necessidade de um gerador.

Exemplo de uso:
    from pypix_api.models.enums import PoliticaRetentativa
    from pypix_api.utils.identificadores import gerar_id_rec

    id_rec = gerar_id_rec('12345678', PoliticaRetentativa.PERMITE_3R_7D)
    # 'RR12345678' + data + sequencial
"""

import secrets
import string
from datetime import date

from pypix_api.models.enums import PoliticaRetentativa

# Alfabeto do sequencial conforme o schema RecId: [a-z|A-Z|0-9]
_ALFABETO_SEQUENCIAL = string.ascii_letters + string.digits

# Tamanhos definidos pela regra de formação RAxxxxxxxxyyyyMMddkkkkkkkkkkk
_TAMANHO_ISPB = 8
_TAMANHO_SEQUENCIAL = 11
_TAMANHO_ID_REC = 29

# Segundo caractere do idRec: indica se a recorrência aceita novas tentativas
# de pagamento pós-vencimento. Precisa ser coerente com politicaRetentativa.
_PREFIXO_POR_POLITICA = {
    PoliticaRetentativa.PERMITE_3R_7D: 'RR',
    PoliticaRetentativa.NAO_PERMITE: 'RN',
}


def gerar_id_rec(
    ispb: str,
    politica_retentativa: PoliticaRetentativa | str,
    data_criacao: date | None = None,
    sequencial: str | None = None,
) -> str:
    """Gera um ``idRec`` válido para criação de recorrência (Pix Automático).

    Monta o identificador conforme a regra de formação do schema ``RecId``::

        RAxxxxxxxxyyyyMMddkkkkkkkkkkk   (29 caracteres, case sensitive)

        R           fixo, recorrência criada dentro do Pix
        A           'R' permite retentativa pós-vencimento, 'N' não permite
        xxxxxxxx    ISPB do participante (8 dígitos)
        yyyyMMdd    data de criação da recorrência
        kkkkkkkkkkk sequencial alfanumérico (11 caracteres)

    O segundo caractere é derivado de ``politica_retentativa``, garantindo que o
    identificador e o campo ``politicaRetentativa`` do corpo da recorrência não
    fiquem contraditórios — uma inconsistência que o schema não detecta.

    Args:
        ispb: ISPB do participante direto/indireto ou os 8 primeiros dígitos do
            CNPJ do prestador de serviço de iniciação. 8 dígitos em ``[0-9]``.
        politica_retentativa: Política de retentativa da recorrência. Aceita um
            membro de :class:`~pypix_api.models.enums.PoliticaRetentativa` ou a
            string equivalente. Deve ser o mesmo valor enviado no corpo.
        data_criacao: Data de criação da recorrência. Padrão: data corrente.
        sequencial: Sequencial de 11 caracteres em ``[a-zA-Z0-9]``, único
            dentro da data de criação. Padrão: gerado aleatoriamente.

    Returns:
        str: identificador de 29 caracteres.

    Raises:
        ValueError: Se o ISPB não tiver 8 dígitos em ``[0-9]``, se a política de
            retentativa for desconhecida ou se o sequencial informado não tiver
            11 caracteres em ``[a-zA-Z0-9]``.

    Nota:
        O sequencial gerado automaticamente é aleatório (62^11 combinações), o
        que torna a colisão dentro de um mesmo dia improvável, mas não
        impossível. Quando houver controle transacional do lado da aplicação,
        informe ``sequencial`` explicitamente.
    """
    # Não usar `str.isdigit()`: ele aceita dígitos não-ASCII (fullwidth, árabe-índicos
    # etc.), que passariam aqui e produziriam um idRec fora de [a-zA-Z0-9]{29}.
    if len(ispb) != _TAMANHO_ISPB or not set(ispb).issubset(string.digits):
        raise ValueError(
            f'ispb deve ter {_TAMANHO_ISPB} dígitos em [0-9], recebido: {ispb!r}'
        )

    try:
        politica = PoliticaRetentativa(politica_retentativa)
    except ValueError as exc:
        validos = ', '.join(membro.value for membro in PoliticaRetentativa)
        raise ValueError(
            f'politica_retentativa inválida: {politica_retentativa!r}. '
            f'Valores aceitos: {validos}'
        ) from exc

    if sequencial is None:
        sequencial = ''.join(
            secrets.choice(_ALFABETO_SEQUENCIAL) for _ in range(_TAMANHO_SEQUENCIAL)
        )
    elif len(sequencial) != _TAMANHO_SEQUENCIAL or not set(sequencial).issubset(
        _ALFABETO_SEQUENCIAL
    ):
        raise ValueError(
            f'sequencial deve ter {_TAMANHO_SEQUENCIAL} caracteres em [a-zA-Z0-9], '
            f'recebido: {sequencial!r}'
        )

    data = data_criacao or date.today()

    return f'{_PREFIXO_POR_POLITICA[politica]}{ispb}{data:%Y%m%d}{sequencial}'
