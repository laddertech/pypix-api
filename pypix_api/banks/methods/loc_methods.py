"""
pypix_api.banks.loc_methods
---------------------------

Este módulo implementa a classe `LocMethods`, que fornece métodos para operações de
gerenciamento de locations (payload) do PIX, conforme especificação do Banco Central do Brasil.

A classe `LocMethods` é utilizada como base para integração com APIs bancárias que suportam
o PIX, permitindo criar, consultar, listar e desvincular locations de QR Codes.
Os métodos abstraem detalhes de requisições HTTP, tratamento de erros e montagem de parâmetros.

Principais funcionalidades:
- Criação de location de payload
- Consulta de location específica por ID
- Listagem de locations por período e filtros
- Desvinculação de txid de uma location

Esta classe é herdada por implementações específicas de bancos (ex: Banco do Brasil, Sicoob).

Dependências:
- session HTTP compatível (ex: requests.Session)
- Métodos auxiliares: `_create_headers()`, `get_base_url()`

Exemplo de uso:
    class MeuBanco(LocMethods):
        ...

    banco = MeuBanco()
    location = banco.criar_location(tipo_cob="cob")
    locations = banco.listar_locations(inicio="2023-01-01T00:00:00Z", fim="2023-01-31T23:59:59Z")
    loc = banco.consultar_location(id_loc=123)
    banco.desvincular_txid_location(id_loc=123)

"""

from typing import Any


class LocMethods:  # pylint: disable=E1101
    """
    Classe que implementa os métodos para operações de location (payload) do PIX.
    Esta classe é herdada pela BankPixAPIBase.
    """

    def criar_location(self, tipo_cob: str) -> dict[str, Any]:
        """
        Criar location do payload.

        Endpoint para criar uma location para um QR Code do PIX.

        Args:
            tipo_cob: Tipo da cobrança ("cob" para imediata, "cobv" para com vencimento)

        Returns:
            dict contendo os dados da location criada, incluindo:
                - id: Identificador da location
                - location: URL da location
                - tipoCob: Tipo da cobrança
                - criacao: Data de criação

        Raises:
            HTTPError: Para erros 400, 403, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/loc'
        body = {'tipoCob': tipo_cob}
        resp = self.session.post(url, headers=headers, json=body)
        self._handle_error_response(resp)
        return resp.json()

    def listar_locations(
        self,
        inicio: str,
        fim: str,
        txid_presente: bool | None = None,
        tipo_cob: str | None = None,
        pagina_atual: int | None = None,
        itens_por_pagina: int | None = None,
    ) -> dict[str, Any]:
        """
        Consultar locations cadastradas.

        Endpoint para consultar locations cadastradas por período e filtros.

        Args:
            inicio: Data de início da consulta (formato ISO RFC 3339)
            fim: Data de fim da consulta (formato ISO RFC 3339)
            txid_presente: Filtro por presença de txid vinculado (opcional)
            tipo_cob: Tipo de cobrança ("cob" ou "cobv") (opcional)
            pagina_atual: Página atual para paginação (padrão: 0)
            itens_por_pagina: Quantidade de itens por página (padrão: 100)

        Returns:
            dict contendo a lista de locations e parâmetros de paginação

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/loc'
        params: dict[str, Any] = {'inicio': inicio, 'fim': fim}

        if txid_presente is not None:
            params['txIdPresente'] = str(txid_presente).lower()
        if tipo_cob:
            params['tipoCob'] = tipo_cob
        if pagina_atual is not None:
            params['paginacao.paginaAtual'] = str(pagina_atual)
        if itens_por_pagina is not None:
            params['paginacao.itensPorPagina'] = str(itens_por_pagina)

        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp)
        return resp.json()

    def consultar_location(self, id_loc: int) -> dict[str, Any]:
        """
        Recuperar location do payload.

        Endpoint para consultar uma location específica pelo seu ID.

        Args:
            id_loc: Identificador da location

        Returns:
            dict contendo os dados da location, incluindo:
                - id: Identificador da location
                - location: URL da location
                - tipoCob: Tipo da cobrança
                - criacao: Data de criação
                - txid: Identificador da transação (se vinculado)

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/loc/{id_loc}'
        resp = self.session.get(url, headers=headers)
        self._handle_error_response(resp)
        return resp.json()

    def desvincular_txid_location(self, id_loc: int) -> dict[str, Any]:
        """
        Desvincular txid de uma location.

        Endpoint para desvincular uma cobrança (txid) de uma location específica.
        A location continua existindo, mas sem cobrança vinculada.

        Args:
            id_loc: Identificador da location

        Returns:
            dict contendo os dados da location após desvinculação

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/loc/{id_loc}/txid'
        resp = self.session.delete(url, headers=headers)
        self._handle_error_response(resp)
        return resp.json()
