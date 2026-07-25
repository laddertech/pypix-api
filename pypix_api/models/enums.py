"""
pypix_api.models.enums
----------------------

Enums com os valores de status definidos pela especificação da API Pix do BACEN.

Os valores são transcritos literalmente do schema oficial (``openapi.yaml``) e
valem para todos os PSPs, já que fazem parte da especificação do BACEN — não há
variação entre Banco do Brasil, Sicoob ou Sicredi.

Cada enum documenta quais valores podem ser **enviados** em uma requisição de
revisão (``PATCH``) e quais são apenas de **leitura** (retornados pelo PSP ou
usados como filtro em listagens).

Exemplo de uso:
    from pypix_api.models.enums import StatusCobR

    # Cancelar uma cobrança recorrente específica
    api.revisar_cobr(txid, {'status': StatusCobR.CANCELADA.value})

Nota sobre serialização:
    Os enums herdam de ``str``, então ``json.dumps`` e a concatenação já produzem
    a string correta. A conversão para texto, porém, não é uniforme — e o
    comportamento de f-strings mudou no Python 3.11::

        x = StatusCobR.CANCELADA

        json.dumps({'status': x})  'CANCELADA'              em todas as versões
        'status=' + x              'status=CANCELADA'       em todas as versões
        str(x)                     'StatusCobR.CANCELADA'   em todas as versões
        f'{x}'                     'CANCELADA'              no 3.10
                                   'StatusCobR.CANCELADA'   no 3.11+

    Por isso, use sempre ``.value`` ao montar corpos de requisição ou mensagens
    de log: é o único acesso que devolve a string da especificação em qualquer
    versão suportada.
"""

from enum import Enum


class StatusCob(str, Enum):
    """Status do registro de uma cobrança imediata (cob) ou com vencimento (cobv).

    Corresponde ao schema ``CobrancaStatus`` da especificação.

    Escrivível em ``PATCH /cob/{txid}`` e ``PATCH /cobv/{txid}``:
        - ``REMOVIDA_PELO_USUARIO_RECEBEDOR``

    Somente leitura (retornados pelo PSP ou usados como filtro em listagens):
        - ``ATIVA``, ``CONCLUIDA``, ``REMOVIDA_PELO_PSP``
    """

    ATIVA = 'ATIVA'
    CONCLUIDA = 'CONCLUIDA'
    REMOVIDA_PELO_USUARIO_RECEBEDOR = 'REMOVIDA_PELO_USUARIO_RECEBEDOR'
    REMOVIDA_PELO_PSP = 'REMOVIDA_PELO_PSP'


class StatusCobR(str, Enum):
    """Status do registro de uma cobrança recorrente (CobR / Pix Automático).

    Corresponde ao schema ``CobRStatus`` da especificação.

    Escrivível em ``PATCH /cobr/{txid}`` (schema ``CobRStatusRevisada``):
        - ``CANCELADA`` — único valor aceito.

    Somente leitura (retornados pelo PSP ou usados como filtro em listagens):
        - ``CRIADA``, ``ATIVA``, ``CONCLUIDA``, ``EXPIRADA``, ``REJEITADA``

    Cancelar uma CobR encerra apenas aquela cobrança do ciclo; a recorrência
    (``rec``) permanece ativa. Para encerrar a recorrência inteira, use
    :class:`StatusRec` com ``PATCH /rec/{idRec}``.
    """

    CRIADA = 'CRIADA'
    ATIVA = 'ATIVA'
    CONCLUIDA = 'CONCLUIDA'
    EXPIRADA = 'EXPIRADA'
    REJEITADA = 'REJEITADA'
    CANCELADA = 'CANCELADA'


class StatusRec(str, Enum):
    """Status do registro de uma recorrência (Rec / Pix Automático).

    Corresponde ao schema ``RecStatus`` da especificação.

    Escrivível em ``PATCH /rec/{idRec}`` (schema ``RecRevisada``):
        - ``CANCELADA`` — único valor aceito.

    Somente leitura (retornados pelo PSP ou usados como filtro em listagens):
        - ``CRIADA``, ``APROVADA``, ``REJEITADA``, ``EXPIRADA``

    Cancelar a recorrência encerra o vínculo por completo, inclusive as
    cobranças futuras. Para cancelar apenas uma cobrança do ciclo, use
    :class:`StatusCobR`.
    """

    CRIADA = 'CRIADA'
    APROVADA = 'APROVADA'
    REJEITADA = 'REJEITADA'
    EXPIRADA = 'EXPIRADA'
    CANCELADA = 'CANCELADA'


class StatusSolicRec(str, Enum):
    """Status de uma solicitação de confirmação de recorrência (SolicRec).

    Corresponde ao schema ``SolicRecStatus`` da especificação.

    Escrivível em ``PATCH /solicrec/{idSolicRec}`` (schema ``SolicRecRevisada``):
        - ``CANCELADA`` — único valor aceito.

    Somente leitura (atribuídos pelo PSP do pagador):
        - ``CRIADA``, ``ENVIADA``, ``RECEBIDA``, ``REJEITADA``, ``ACEITA``,
          ``EXPIRADA``

    Atenção: ``REJEITADA`` é um status de resposta — nunca deve ser enviado em
    uma revisão.
    """

    CRIADA = 'CRIADA'
    ENVIADA = 'ENVIADA'
    RECEBIDA = 'RECEBIDA'
    REJEITADA = 'REJEITADA'
    ACEITA = 'ACEITA'
    EXPIRADA = 'EXPIRADA'
    CANCELADA = 'CANCELADA'


class PoliticaRetentativa(str, Enum):
    """Política de retentativa de uma recorrência ou cobrança recorrente.

    Corresponde aos schemas ``RecConfiguracao`` e ``CobRConfiguracao``.

    Valores:
        - ``NAO_PERMITE``: não é permitida retentativa de liquidação.
        - ``PERMITE_3R_7D``: permite até 3 retentativas em até 7 dias.

    Uma CobR só aceita ``POST /cobr/{txid}/retentativa/{data}`` se a recorrência
    estiver configurada com ``PERMITE_3R_7D``.
    """

    NAO_PERMITE = 'NAO_PERMITE'
    PERMITE_3R_7D = 'PERMITE_3R_7D'
