Pix Automático (Recorrência)
============================

Este guia mostra o fluxo de Pix Automático — recorrência (``rec``), solicitação
de confirmação (``solicrec``) e cobranças recorrentes (``cobr``) — com ênfase no
cancelamento, que é a operação onde mais se erra o valor do status.

.. note::
   Para cobranças com data de vencimento **sem** recorrência (``cobv``), veja
   :doc:`recurring`.

Status disponíveis
------------------

Os status são definidos pela especificação do BACEN e valem para todos os PSPs
(Banco do Brasil, Sicoob e Sicredi). A biblioteca expõe todos eles como enums:

.. code-block:: python

    from pypix_api.models.enums import (
        PoliticaRetentativa,
        StatusCob,
        StatusCobR,
        StatusRec,
        StatusSolicRec,
    )

.. list-table::
   :header-rows: 1
   :widths: 20 45 35

   * - Enum
     - Valores
     - Aceito em PATCH
   * - ``StatusCob``
     - ``ATIVA``, ``CONCLUIDA``, ``REMOVIDA_PELO_USUARIO_RECEBEDOR``,
       ``REMOVIDA_PELO_PSP``
     - ``REMOVIDA_PELO_USUARIO_RECEBEDOR``
   * - ``StatusCobR``
     - ``CRIADA``, ``ATIVA``, ``CONCLUIDA``, ``EXPIRADA``, ``REJEITADA``,
       ``CANCELADA``
     - ``CANCELADA``
   * - ``StatusRec``
     - ``CRIADA``, ``APROVADA``, ``REJEITADA``, ``EXPIRADA``, ``CANCELADA``
     - ``CANCELADA``
   * - ``StatusSolicRec``
     - ``CRIADA``, ``ENVIADA``, ``RECEBIDA``, ``REJEITADA``, ``ACEITA``,
       ``EXPIRADA``, ``CANCELADA``
     - ``CANCELADA``

Os demais valores são atribuídos pelo PSP e só aparecem em respostas ou como
filtro em listagens. Em particular, ``REJEITADA`` **nunca** deve ser enviado em
uma revisão — é a decisão do PSP do pagador.

Fluxo completo
--------------

As três etapas são encadeadas: a recorrência (``rec``) estabelece o vínculo, a
solicitação (``solicrec``) leva esse vínculo ao pagador para autorização, e só
então as cobranças (``cobr``) de cada ciclo podem ser liquidadas. Pular o
``solicrec`` deixa a recorrência parada em ``CRIADA``.

.. code-block:: python

    import uuid
    from datetime import date, timedelta

    from pypix_api.auth.oauth2 import OAuth2Client
    from pypix_api.banks.sicredi import SicrediPixAPI
    from pypix_api.models.enums import PoliticaRetentativa, StatusRec
    from pypix_api.utils.identificadores import gerar_id_rec

    oauth = OAuth2Client(
        token_url=SicrediPixAPI.TOKEN_URL,
        client_id='seu_client_id',
        client_secret='seu_client_secret',
        cert='certificado.pem',
        pvk='chave.key',
    )
    api = SicrediPixAPI(oauth=oauth)

    # 1. Criar a recorrência (o vínculo com o pagador)
    #    O idRec tem regra de formação semântica — veja a seção abaixo.
    politica = PoliticaRetentativa.PERMITE_3R_7D
    id_rec = gerar_id_rec(ispb='12345678', politica_retentativa=politica)

    rec = api.criar_recorrencia({
        'idRec': id_rec,
        'vinculo': {
            'contrato': 'CT-2026-0001',
            'devedor': {'cpf': '12345678909', 'nome': 'Fulano de Tal'},
            'objeto': 'Assinatura mensal',
        },
        'calendario': {
            'dataInicial': str(date.today() + timedelta(days=7)),
            'periodicidade': 'MENSAL',
        },
        'valor': {'valorRec': '49.90'},
        'politicaRetentativa': politica.value,
        'ativacao': {'dadosJornada': {'txid': uuid.uuid4().hex}},
    })

    # 2. Solicitar a confirmação ao pagador
    #    Sem esta etapa a recorrência permanece CRIADA e não é autorizada.
    solic = api.criar_solicrec({
        'idRec': id_rec,
        'calendario': {
            'dataExpiracaoSolicitacao': (
                f'{date.today() + timedelta(days=3)}T23:59:59Z'
            ),
        },
        'destinatario': {
            'ispbParticipante': '91193552',
            'agencia': '2569',
            'conta': '550689',
            'cpf': '12345678909',
        },
    })
    id_solic_rec = solic['idSolicRec']

    # 3. Acompanhar até o pagador aceitar (status ACEITA) e a rec ficar APROVADA
    #    Na prática, use o webhook de recorrência em vez de consultar em laço.
    if api.consultar_recorrencia(id_rec)['status'] == StatusRec.APROVADA:
        ...

    # 4. Emitir uma cobrança do ciclo
    txid = uuid.uuid4().hex
    cobr = api.criar_cobr_com_txid(txid, {
        'idRec': id_rec,
        'calendario': {'dataDeVencimento': str(date.today() + timedelta(days=10))},
        'valor': {'original': '49.90'},
        'recebedor': {'agencia': '1234', 'conta': '567890', 'tipoConta': 'CORRENTE'},
        'ajusteDiaUtil': True,
    })

O identificador da recorrência (idRec)
--------------------------------------

O ``idRec`` não é um identificador livre. O schema ``RecId`` define uma regra de
formação com significado em cada trecho::

    RAxxxxxxxxyyyyMMddkkkkkkkkkkk   (29 caracteres, case sensitive)

    R           fixo, recorrência criada dentro do Pix
    A           'R' permite retentativa pós-vencimento, 'N' não permite
    xxxxxxxx    ISPB do participante (8 dígitos)
    yyyyMMdd    data de criação da recorrência
    kkkkkkkkkkk sequencial alfanumérico (11 caracteres), único no dia

.. warning::
   Um valor aleatório de 29 caracteres alfanuméricos **passa** na validação de
   formato do schema (``pattern: [a-zA-Z0-9]{29}``) e ainda assim é recusado
   pelo PSP, porque o ISPB e a data precisam ser reais. Da mesma forma, o
   segundo caractere precisa ser coerente com ``politicaRetentativa``: usar
   ``RR`` (permite) junto de ``NAO_PERMITE`` gera uma contradição que nenhum
   schema detecta.

Use :func:`~pypix_api.utils.identificadores.gerar_id_rec`, que deriva o segundo
caractere da própria política, eliminando a inconsistência:

.. code-block:: python

    from pypix_api.models.enums import PoliticaRetentativa
    from pypix_api.utils.identificadores import gerar_id_rec

    gerar_id_rec('12345678', PoliticaRetentativa.PERMITE_3R_7D)
    # 'RR12345678' + data de hoje + sequencial aleatório

    gerar_id_rec('12345678', PoliticaRetentativa.NAO_PERMITE)
    # 'RN12345678' + data de hoje + sequencial aleatório

    # Com sequencial e data explícitos (quando há controle transacional)
    gerar_id_rec(
        ispb='12345678',
        politica_retentativa=PoliticaRetentativa.PERMITE_3R_7D,
        data_criacao=date(2026, 7, 25),
        sequencial='abcdefghijk',
    )
    # 'RR1234567820260725abcdefghijk'

O ``ispb`` é o do participante direto ou indireto, ou os 8 primeiros dígitos do
CNPJ do prestador de serviço de iniciação — obtenha-o com seu PSP. O sequencial
gerado automaticamente é aleatório entre 62^11 combinações; se a aplicação tiver
controle transacional, informe-o explicitamente para garantir unicidade no dia.

Cancelar uma cobrança sem cancelar a recorrência
------------------------------------------------

Esta é a distinção que mais gera confusão. São recursos diferentes:

.. code-block:: python

    # Cancela SOMENTE a cobrança deste ciclo.
    # A recorrência segue ativa e os próximos ciclos continuam sendo cobrados.
    api.cancelar_cobr(txid)

    # Encerra a recorrência INTEIRA, incluindo as cobranças futuras.
    api.cancelar_recorrencia(id_rec)

    # Cancela a solicitação de confirmação enviada ao pagador.
    api.cancelar_solicrec(id_solic_rec)

Os três helpers são atalhos para os métodos ``revisar_*``, que também podem ser
chamados diretamente com o corpo montado à mão:

.. code-block:: python

    from pypix_api.models.enums import StatusCobR

    api.revisar_cobr(txid, {'status': StatusCobR.CANCELADA.value})

O corpo é plano e tem um único campo — o schema ``CobRStatusRevisada`` não
aceita nenhum outro:

.. code-block:: json

    {"status": "CANCELADA"}

.. warning::
   O PSP recusa o cancelamento com **HTTP 400** quando a data corrente é igual
   ou posterior à data prevista da primeira tentativa de liquidação. Não existe
   janela em dias — o corte é essa data. Cancele antes que o ciclo entre em
   liquidação.

Uma CobR ``CANCELADA`` (ou ``REJEITADA``) libera o ciclo, permitindo emitir uma
nova cobrança para o mesmo ``idRec`` com a mesma ``dataDeVencimento``.

Consultar o status
------------------

Como os enums herdam de ``str``, a comparação com a resposta crua da API
funciona diretamente:

.. code-block:: python

    from pypix_api.models.enums import StatusCobR

    cobr = api.consultar_cobr(txid)

    if cobr['status'] == StatusCobR.CANCELADA:
        print('Cobrança cancelada')
    elif cobr['status'] == StatusCobR.CONCLUIDA:
        print('Cobrança liquidada')

Retentativa
-----------

Só é possível solicitar retentativa se a recorrência tiver sido criada com
``PoliticaRetentativa.PERMITE_3R_7D`` (até 3 retentativas em até 7 dias):

.. code-block:: python

    api.solicitar_retentativa_cobr(txid, date.today() + timedelta(days=2))
