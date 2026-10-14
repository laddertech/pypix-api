"""
pypix_api.banks.methods.pix_inter_methods
-----------------------------------------

Este módulo implementa a classe `PixInterMethods`, com os endpoints exclusivos
do Banco Inter, fora da especificação padrão do Banco Central:

- Consulta e reenvio de callbacks de webhook (``/webhook/callbacks``)
- Simulações do ambiente Sandbox: pagamento de cobranças (imediata, com
  vencimento, por QR Code e recorrente) e mudança de status de recorrência,
  solicitação de recorrência e cobrança recorrente

IMPORTANTE: Esta classe deve ser usada APENAS com a implementação InterPixAPI.
Os métodos ``sandbox_*`` só existem no ambiente Sandbox do Inter e recusam a
chamada quando a instância não foi construída com ``homologacao=True``.

Dependências:
- Métodos auxiliares `_request()`, `_json()` e `_json_opcional()`, fornecidos
  por `BankPixAPIBase`
- Métodos `_exige_sandbox()` e `_exige_producao()`, fornecidos por `InterPixAPI`

Exemplo de uso::

    from pypix_api.banks.inter import InterPixAPI

    inter = InterPixAPI(oauth=oauth_client, homologacao=True)
    inter.criar_cob('txid...', body)
    inter.sandbox_pagar_cob('txid...', valor=10.50)
    callbacks = inter.consultar_callbacks_webhook(
        data_hora_inicio='2025-01-01T00:00:00Z',
        data_hora_fim='2025-01-31T23:59:59Z',
    )

"""

from decimal import Decimal
from typing import Any

#: Limite de txids por chamada de reenvio de callbacks, segundo a especificação.
MAX_TXIDS_REENVIO = 50


class PixInterMethods:  # pylint: disable=E1101
    """
    Classe que implementa os métodos exclusivos do Banco Inter para operações de PIX.
    Esta classe é herdada APENAS pela InterPixAPI.
    """

    # --- Callbacks de webhook ---------------------------------------------------

    def consultar_callbacks_webhook(
        self,
        data_hora_inicio: str,
        data_hora_fim: str,
        pagina: int | None = None,
        tamanho_pagina: int | None = None,
        txid: str | None = None,
    ) -> dict[str, Any]:
        """Consultar callbacks de webhook (endpoint exclusivo Inter).

        Retorna as requisições de callback ordenadas pela data de disparo
        (decrescente). Útil para investigar falhas na entrega de notificações.

        Args:
            data_hora_inicio: Início do período (formato ISO RFC 3339)
            data_hora_fim: Fim do período (formato ISO RFC 3339)
            pagina: Posição da página na lista (padrão do PSP: 0)
            tamanho_pagina: Itens por página, entre 10 e 50 (padrão do PSP: 20)
            txid: Filtra os callbacks de um pagamento específico

        Returns:
            dict com a lista paginada de callbacks
        """
        params: dict[str, Any] = {
            'dataHoraInicio': data_hora_inicio,
            'dataHoraFim': data_hora_fim,
        }
        if pagina is not None:
            params['pagina'] = pagina
        if tamanho_pagina is not None:
            params['tamanhoPagina'] = tamanho_pagina
        if txid:
            params['txid'] = txid

        resp = self._request('GET', '/webhook/callbacks', params=params)
        return self._json(resp)

    def reenviar_callbacks_webhook(
        self, txids: str | list[str], chave_pix: str
    ) -> dict[str, Any]:
        """Reenviar callbacks de webhook (endpoint exclusivo Inter).

        A especificação documenta este endpoint apenas no servidor de produção,
        por isso a chamada é recusada no Sandbox.

        Args:
            txids: Txid, ou lista de até 50 txids, cujos callbacks serão
                reenviados
            chave_pix: Chave Pix usada nas transações — a mesma para todos os
                txids

        Returns:
            dict com o retorno do PSP (vazio quando a resposta não tem corpo)

        Raises:
            ValueError: Se a instância apontar para o Sandbox, se não houver
                txid ou se houver mais de 50
        """
        self._exige_producao('reenviar_callbacks_webhook')
        # Uma string avulsa vira lista de um item: `list('abc')` separaria os
        # caracteres e reenviaria txids inexistentes.
        lista = [txids] if isinstance(txids, str) else list(txids)
        if not lista:
            raise ValueError('Informe ao menos um txid para reenviar os callbacks.')
        if len(lista) > MAX_TXIDS_REENVIO:
            raise ValueError(
                f'No máximo {MAX_TXIDS_REENVIO} txids por chamada; '
                f'recebidos {len(lista)}.'
            )

        body = {'txId': lista, 'chavePix': chave_pix}
        resp = self._request('POST', '/webhook/callbacks/retry', json=body)
        return self._json_opcional(resp)

    # --- Simulações do Sandbox --------------------------------------------------

    def sandbox_pagar_cob(self, txid: str, valor: float | Decimal) -> dict[str, Any]:
        """Pagar uma cobrança imediata (exclusivo do Sandbox Inter).

        Args:
            txid: Identificador da cobrança
            valor: Valor a pagar

        Returns:
            dict com o retorno do PSP (vazio quando a resposta não tem corpo)
        """
        self._exige_sandbox('sandbox_pagar_cob')
        resp = self._request(
            'POST', f'/cob/pagar/{txid}', json={'valor': _numero(valor)}
        )
        return self._json_opcional(resp)

    def sandbox_pagar_cobv(self, txid: str, valor: float | Decimal) -> dict[str, Any]:
        """Pagar uma cobrança com vencimento (exclusivo do Sandbox Inter).

        Args:
            txid: Identificador da cobrança
            valor: Valor a pagar

        Returns:
            dict com o retorno do PSP (vazio quando a resposta não tem corpo)
        """
        self._exige_sandbox('sandbox_pagar_cobv')
        resp = self._request(
            'POST', f'/cobv/pagar/{txid}', json={'valor': _numero(valor)}
        )
        return self._json_opcional(resp)

    def sandbox_pagar_qrcode(
        self, qr_code: str, valor: float | Decimal
    ) -> dict[str, Any]:
        """Pagar via QR Code (exclusivo do Sandbox Inter).

        Paga uma cobrança imediata ou com vencimento a partir do Pix Copia e
        Cola; num QR Code de recorrência com cobrança vinculada, também
        autoriza a recorrência.

        Args:
            qr_code: Conteúdo do Pix Copia e Cola
            valor: Valor a pagar

        Returns:
            dict com o retorno do PSP (vazio quando a resposta não tem corpo)
        """
        self._exige_sandbox('sandbox_pagar_qrcode')
        body = {'qrCode': qr_code, 'valor': _numero(valor)}
        resp = self._request('POST', '/sandbox/cob/pagamento', json=body)
        return self._json_opcional(resp)

    def sandbox_pagar_cobr(
        self, txid: str, valor: float | Decimal, cpf_cnpj: str, chave: str
    ) -> dict[str, Any]:
        """Pagar uma cobrança recorrente (exclusivo do Sandbox Inter).

        Args:
            txid: Identificador da cobrança recorrente
            valor: Valor a pagar
            cpf_cnpj: CPF ou CNPJ do pagador
            chave: Chave Pix do recebedor

        Returns:
            dict com o retorno do PSP (vazio quando a resposta não tem corpo)
        """
        self._exige_sandbox('sandbox_pagar_cobr')
        body = {
            'valor': _numero(valor),
            'cpfCnpj': cpf_cnpj,
            'txId': txid,
            'chave': chave,
        }
        resp = self._request('POST', '/sandbox/cobr/pagamento', json=body)
        return self._json_opcional(resp)

    def sandbox_alterar_status_rec(
        self, id_rec: str, status: str, razao: str | None = None
    ) -> dict[str, Any]:
        """Alterar o status de uma recorrência (exclusivo do Sandbox Inter).

        A aprovação da recorrência é necessária para criar cobranças
        recorrentes no Sandbox.

        Args:
            id_rec: Identificador da recorrência
            status: ``'APROVADA'`` ou ``'CANCELADA'``
            razao: Motivo da mudança (``ACCL``, ``CPCL``, ``DCSD``, ``ERSL``,
                ``FRUD``, ``PCFD``, ``SLCR``, ``SLDB`` ou ``NRES``)

        Returns:
            dict com o retorno do PSP (vazio quando a resposta não tem corpo)
        """
        self._exige_sandbox('sandbox_alterar_status_rec')
        body: dict[str, Any] = {'status': status}
        if razao:
            body['razao'] = razao
        resp = self._request('PATCH', f'/sandbox/rec/{id_rec}/status', json=body)
        return self._json_opcional(resp)

    def sandbox_alterar_status_solicrec(
        self, id_rec: str, status: str
    ) -> dict[str, Any]:
        """Simular o aceite ou a rejeição de uma solicitação de recorrência
        pelo pagador (exclusivo do Sandbox Inter).

        Args:
            id_rec: Identificador informado no caminho
                ``/sandbox/solicrec/{idRec}/status`` — a especificação o nomeia
                ``idRec``
            status: ``'ACEITA'`` ou ``'REJEITADA'``

        Returns:
            dict com o retorno do PSP (vazio quando a resposta não tem corpo)
        """
        self._exige_sandbox('sandbox_alterar_status_solicrec')
        resp = self._request(
            'PATCH', f'/sandbox/solicrec/{id_rec}/status', json={'status': status}
        )
        return self._json_opcional(resp)

    def sandbox_cancelar_cobr(self, txid: str, razao: str) -> dict[str, Any]:
        """Cancelar uma cobrança recorrente por estímulo externo (exclusivo do
        Sandbox Inter).

        Args:
            txid: Identificador da cobrança recorrente
            razao: Motivo (``UNSPECIFIED``, ``ACCOUNT_CANCELED``,
                ``ACCOUNT_BLOCKED``, ``RECURRENCE_CANCELED``,
                ``SETTLEMENT_FAILED``, ``OTHER``, ``REQUESTED_BY_PAYER`` ou
                ``REQUESTED_BY_RECEIVER``)

        Returns:
            dict com o retorno do PSP (vazio quando a resposta não tem corpo)
        """
        self._exige_sandbox('sandbox_cancelar_cobr')
        body = {'status': 'CANCELADA', 'razao': razao}
        resp = self._request('PATCH', f'/sandbox/cobr/{txid}/status', json=body)
        return self._json_opcional(resp)


def _numero(valor: float | Decimal) -> float:
    """Converte o valor para o ``number`` JSON que a especificação pede.

    ``Decimal`` não é serializável pelo ``json`` do ``requests``.
    """
    return float(valor)
