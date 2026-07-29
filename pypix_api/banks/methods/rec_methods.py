"""
Módulo para métodos de recorrência da API Pix.

Este módulo implementa os métodos relacionados ao gerenciamento de recorrências
conforme especificado na API OpenAPI. Inclui operações para:
- Criar recorrências
- Consultar recorrência específica
- Revisar recorrências existentes
- Cancelar recorrências
- Listar recorrências com filtros

Classes:
    RecMethods: Classe base com métodos para operações de recorrência
"""

from typing import Any

from pypix_api.models.enums import StatusRec


class RecMethods:  # pylint: disable=E1101
    """
    Classe que implementa métodos para operações de recorrência da API Pix.

    Esta classe fornece métodos para gerenciar recorrências, incluindo criação,
    consulta, revisão e listagem de recorrências com diversos filtros disponíveis.
    """

    def criar_recorrencia(self, body: dict[str, Any]) -> dict[str, Any]:
        """
        Criar uma nova recorrência.

        Endpoint para criar uma recorrência via POST /rec.
        O idRec deve ser informado no corpo da requisição.

        Args:
            body: Dados da recorrência contendo obrigatoriamente o idRec

        Returns:
            dict contendo os dados da recorrência criada

        Raises:
            HTTPError: Para erros 400, 403, 503
        """
        resp = self._request('POST', '/rec', json=body)
        return self._json(resp)

    def revisar_recorrencia(self, id_rec: str, body: dict[str, Any]) -> dict[str, Any]:
        """
        Revisar uma recorrência existente.

        Endpoint PATCH /rec/{idRec}. O schema ``RecRevisada`` aceita, além do
        status, os campos ``vinculo.devedor.nome``, ``loc``,
        ``calendario.dataInicial`` e ``ativacao.dadosJornada.txid``.

        O único status aceito é ``CANCELADA``::

            api.revisar_recorrencia(id_rec, {'status': StatusRec.CANCELADA.value})

        Para cancelar, prefira :meth:`cancelar_recorrencia`, que monta o corpo.
        Cancelar a recorrência encerra o vínculo por completo, incluindo as
        cobranças futuras. Para cancelar apenas uma cobrança do ciclo, use
        :meth:`~pypix_api.banks.methods.cobr_methods.CobRMethods.cancelar_cobr`.

        O PSP recusa a revisão (HTTP 400) se a recorrência já estiver expirada,
        cancelada ou rejeitada. Os campos ``loc`` e ``calendario.dataInicial``
        só podem ser alterados enquanto o status for ``CRIADA``.

        Args:
            id_rec: Identificador da recorrência
            body: Dados para revisão da recorrência

        Returns:
            dict contendo os dados da recorrência revisada

        Raises:
            HTTPError: Para erros 400, 403, 404, 503
        """
        resp = self._request('PATCH', f'/rec/{id_rec}', json=body)
        return self._json(resp)

    def cancelar_recorrencia(self, id_rec: str) -> dict[str, Any]:
        """
        Cancelar uma recorrência por completo.

        Atalho para :meth:`revisar_recorrencia` com ``{'status': 'CANCELADA'}``.

        Encerra o vínculo de recorrência e, com ele, as cobranças dos ciclos
        seguintes. Para cancelar apenas uma cobrança específica mantendo a
        recorrência ativa, use
        :meth:`~pypix_api.banks.methods.cobr_methods.CobRMethods.cancelar_cobr`.

        Args:
            id_rec: Identificador da recorrência

        Returns:
            dict contendo os dados da recorrência cancelada

        Raises:
            HTTPError: Para erros 400, 403, 404, 503. O PSP retorna 400 quando a
                recorrência já se encontra expirada, cancelada ou rejeitada.
        """
        return self.revisar_recorrencia(id_rec, {'status': StatusRec.CANCELADA.value})

    def consultar_recorrencia(
        self, id_rec: str, txid: str | None = None
    ) -> dict[str, Any]:
        """
        Consultar uma recorrência específica.
        """
        params = {}
        if txid:
            params['txid'] = txid
        resp = self._request('GET', f'/rec/{id_rec}', params=params)
        return self._json(resp)

    def listar_recorrencias(
        self,
        inicio: str,
        fim: str,
        cpf: str | None = None,
        cnpj: str | None = None,
        location_presente: bool | None = None,
        status: str | None = None,
        convenio: str | None = None,
        pagina_atual: int | None = None,
        itens_por_pagina: int | None = None,
    ) -> dict[str, Any]:
        """
        Consultar lista de recorrências com filtros.
        """
        if cpf and cnpj:
            raise ValueError('CPF e CNPJ não podem ser utilizados simultaneamente')

        params = {'inicio': inicio, 'fim': fim}
        if cpf:
            params['cpf'] = cpf
        if cnpj:
            params['cnpj'] = cnpj
        if location_presente is not None:
            params['locationPresente'] = str(location_presente).lower()
        if status:
            params['status'] = status
        if convenio:
            params['convenio'] = convenio
        if pagina_atual is not None:
            params['paginacao.paginaAtual'] = str(pagina_atual)
        if itens_por_pagina is not None:
            params['paginacao.itensPorPagina'] = str(itens_por_pagina)

        resp = self._request('GET', '/rec', params=params)
        return self._json(resp)
