"""
pypix_api.banks.locrec_methods
------------------------------

Este módulo implementa a classe `LocRecMethods`, que fornece métodos para operações de
gerenciamento de locations de recorrência do PIX, conforme especificação do Banco Central.

A classe `LocRecMethods` é utilizada como base para integração com APIs bancárias que suportam
o PIX Automático/Recorrente, permitindo criar, consultar, listar e desvincular locations
de recorrência. Os métodos abstraem detalhes de requisições HTTP e tratamento de erros.

Principais funcionalidades:
- Criação de location de recorrência
- Consulta de location de recorrência específica por ID
- Listagem de locations de recorrência por período e filtros
- Desvinculação de idRec de uma location de recorrência

Esta classe é herdada por implementações específicas de bancos (ex: Banco do Brasil).

Dependências:
- session HTTP compatível (ex: requests.Session)
- Métodos auxiliares: `_create_headers()`, `get_base_url()`

Exemplo de uso:
    class MeuBanco(LocRecMethods):
        ...

    banco = MeuBanco()
    location = banco.criar_location_rec()
    locations = banco.listar_locations_rec(inicio="2023-01-01T00:00:00Z", fim="2023-01-31T23:59:59Z")
    loc = banco.consultar_location_rec(id_loc=123)
    banco.desvincular_idrec_location(id_loc=123)

"""

from typing import Any


class LocRecMethods:  # pylint: disable=E1101
    """
    Classe que implementa os métodos para operações de location de recorrência do PIX.
    Esta classe é herdada pela BankPixAPIBase.
    """

    def criar_location_rec(self) -> dict[str, Any]:
        """
        Criar location de recorrência.

        Endpoint para criar uma location para recorrência do PIX Automático.

        Returns:
            dict contendo os dados da location criada, incluindo:
                - id: Identificador da location
                - location: URL da location
                - criacao: Data de criação

        Raises:
            HTTPError: Para erros 400, 403, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/locrec'
        resp = self.session.post(url, headers=headers, json={})
        self._handle_error_response(resp)
        return resp.json()

    def listar_locations_rec(
        self,
        inicio: str,
        fim: str,
        id_rec_presente: bool | None = None,
        pagina_atual: int | None = None,
        itens_por_pagina: int | None = None,
    ) -> dict[str, Any]:
        """
        Consultar locations de recorrência cadastradas.

        Endpoint para consultar locations de recorrência cadastradas por período e filtros.

        Args:
            inicio: Data de início da consulta (formato ISO RFC 3339)
            fim: Data de fim da consulta (formato ISO RFC 3339)
            id_rec_presente: Filtro por presença de idRec vinculado (opcional)
            pagina_atual: Página atual para paginação (padrão: 0)
            itens_por_pagina: Quantidade de itens por página (padrão: 100)

        Returns:
            dict contendo a lista de locations e parâmetros de paginação

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/locrec'
        params: dict[str, Any] = {'inicio': inicio, 'fim': fim}

        if id_rec_presente is not None:
            params['idRecPresente'] = str(id_rec_presente).lower()
        if pagina_atual is not None:
            params['paginacao.paginaAtual'] = str(pagina_atual)
        if itens_por_pagina is not None:
            params['paginacao.itensPorPagina'] = str(itens_por_pagina)

        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp)
        return resp.json()

    def consultar_location_rec(self, id_loc: int) -> dict[str, Any]:
        """
        Recuperar location de recorrência.

        Endpoint para consultar uma location de recorrência específica pelo seu ID.

        Args:
            id_loc: Identificador da location de recorrência

        Returns:
            dict contendo os dados da location, incluindo:
                - id: Identificador da location
                - location: URL da location
                - criacao: Data de criação
                - idRec: Identificador da recorrência (se vinculado)

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/locrec/{id_loc}'
        resp = self.session.get(url, headers=headers)
        self._handle_error_response(resp)
        return resp.json()

    def desvincular_idrec_location(self, id_loc: int) -> dict[str, Any]:
        """
        Desvincular idRec de uma location de recorrência.

        Endpoint para desvincular uma recorrência (idRec) de uma location específica.
        A location continua existindo, mas sem recorrência vinculada.

        Args:
            id_loc: Identificador da location de recorrência

        Returns:
            dict contendo os dados da location após desvinculação

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        headers = self._create_headers()
        url = f'{self.get_base_url()}/locrec/{id_loc}/idRec'
        resp = self.session.delete(url, headers=headers)
        self._handle_error_response(resp)
        return resp.json()
