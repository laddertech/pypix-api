"""
pypix_api.banks.pix_methods
---------------------------

Este módulo implementa a classe `PixMethods`, que fornece métodos para operações de PIX, conforme especificação do Banco Central do Brasil.

A classe `PixMethods` é utilizada como base para integração com APIs bancárias que suportam o PIX, permitindo consultar PIX recebidos e outras operações relacionadas. Os métodos abstraem detalhes de requisições HTTP, tratamento de erros e montagem de parâmetros, facilitando a integração de sistemas Python com provedores bancários.

Principais funcionalidades:
- Consulta de PIX recebidos por período e filtros

Esta classe é herdada por implementações específicas de bancos (ex: Banco do Brasil, Sicoob).

Dependências:
- session HTTP compatível (ex: requests.Session)
- Métodos auxiliares: `_create_headers()`, `get_base_url()`

Exemplo de uso:
    class MeuBanco(PixMethods):
        ...

    banco = MeuBanco()
    resposta = banco.consultar_pix(inicio="2023-01-01T00:00:00Z", fim="2023-01-31T23:59:59Z")

"""

from typing import Any


class PixMethods:  # pylint: disable=E1101
    """
    Classe que implementa os métodos para operações de PIX.
    Esta classe é herdada pela BankPixAPIBase.
    """

    def consultar_pix(
        self,
        inicio: str,
        fim: str,
        txid: str | None = None,
        txid_presente: bool | None = None,
        devolucao_presente: bool | None = None,
        cpf: str | None = None,
        cnpj: str | None = None,
        pagina_atual: int | None = None,
        itens_por_pagina: int | None = None,
    ) -> dict[str, Any]:
        """
        Consultar PIX recebidos.

        Endpoint para consultar PIX recebidos através de parâmetros como
        início, fim, txid, cpf, cnpj e outros filtros.

        Args:
            inicio: Data de início da consulta (formato ISO)
            fim: Data de fim da consulta (formato ISO)
            txid: Identificador da transação (opcional)
            txid_presente: Filtro por presença de txid (opcional)
            devolucao_presente: Filtro por presença de devolução (opcional)
            cpf: CPF do devedor (11 dígitos). Não pode ser usado com CNPJ
            cnpj: CNPJ do devedor (14 dígitos). Não pode ser usado com CPF
            pagina_atual: Página atual para paginação (padrão: 0)
            itens_por_pagina: Quantidade de itens por página (padrão: 100)

        Returns:
            dict contendo a lista de PIX recebidos

        Raises:
            HTTPError: Para erros 403, 503
            ValueError: Se CPF e CNPJ forem informados simultaneamente
        """
        if cpf and cnpj:
            raise ValueError('CPF e CNPJ não podem ser utilizados simultaneamente')

        headers = self._create_headers()
        url = f'{self.get_base_url()}/pix'
        params = {'inicio': inicio, 'fim': fim}

        # Adiciona parâmetros opcionais se fornecidos
        if txid:
            params['txid'] = txid
        if txid_presente is not None:
            params['txIdPresente'] = txid_presente
        if devolucao_presente is not None:
            params['devolucaoPresente'] = devolucao_presente
        if cpf:
            params['cpf'] = cpf
        if cnpj:
            params['cnpj'] = cnpj
        if pagina_atual is not None:
            params['paginacao.paginaAtual'] = pagina_atual
        if itens_por_pagina is not None:
            params['paginacao.itensPorPagina'] = itens_por_pagina

        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp)
        return resp.json()
