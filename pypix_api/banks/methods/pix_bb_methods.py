"""
pypix_api.banks.pix_bb_methods
------------------------------

Este módulo implementa a classe `PixBBMethods`, que fornece métodos exclusivos do Banco do Brasil
para operações avançadas de PIX, não disponíveis na especificação padrão do Banco Central.

A classe `PixBBMethods` é um mixin específico do BB que adiciona funcionalidades extras como:
- Consulta de PIX recebidos com filtros avançados (chave, contestação)
- Consulta de devoluções com filtros específicos

IMPORTANTE: Esta classe deve ser usada APENAS com a implementação BBPixAPI,
pois os endpoints /pix-bb são exclusivos do Banco do Brasil.

Dependências:
- session HTTP compatível (ex: requests.Session)
- Métodos auxiliares: `_create_headers()`, `get_base_url()`

Exemplo de uso:
    from pypix_api.banks.bb import BBPixAPI

    bb = BBPixAPI(oauth=oauth_client)
    pix = bb.consultar_pix_bb(
        inicio="2023-01-01T00:00:00Z",
        fim="2023-01-31T23:59:59Z",
        chave="email@exemplo.com"
    )
    devolucoes = bb.consultar_devolucoes_bb(
        inicio="2023-01-01T00:00:00Z",
        fim="2023-01-31T23:59:59Z",
        estado_devolucao="DEVOLVIDO"
    )

"""

from typing import Any


class PixBBMethods:  # pylint: disable=E1101
    """
    Classe que implementa os métodos exclusivos do Banco do Brasil para operações de PIX.
    Esta classe é herdada APENAS pela BBPixAPI.

    NOTA: Os endpoints /pix-bb são exclusivos do Banco do Brasil e não fazem parte
    da especificação padrão do Banco Central para a API PIX.
    """

    def _build_pix_bb_params(
        self,
        inicio: str | None,
        fim: str | None,
        txid: str | None,
        txid_presente: bool | None,
        devolucao_presente: bool | None,
        contestacao_presente: bool | None,
        cpf: str | None,
        cnpj: str | None,
        chave: str | None,
        pagina_atual: int | None,
        itens_por_pagina: int | None,
    ) -> dict[str, Any]:
        """Constrói os parâmetros para consulta PIX-BB."""
        params: dict[str, Any] = {}

        # Parâmetros de string simples
        param_mapping = {
            'inicio': inicio,
            'fim': fim,
            'txid': txid,
            'cpf': cpf,
            'cnpj': cnpj,
            'chave': chave,
        }
        for key, value in param_mapping.items():
            if value:
                params[key] = value

        # Parâmetros booleanos
        bool_mapping: dict[str, bool | None] = {
            'txIdPresente': txid_presente,
            'devolucaoPresente': devolucao_presente,
            'contestacaoPresente': contestacao_presente,
        }
        for key, bool_value in bool_mapping.items():
            if bool_value is not None:
                params[key] = str(bool_value).lower()

        # Parâmetros de paginação
        if pagina_atual is not None:
            params['paginacao.paginaAtual'] = str(pagina_atual)
        if itens_por_pagina is not None:
            params['paginacao.itensPorPagina'] = str(itens_por_pagina)

        return params

    def consultar_pix_bb(
        self,
        inicio: str | None = None,
        fim: str | None = None,
        txid: str | None = None,
        txid_presente: bool | None = None,
        devolucao_presente: bool | None = None,
        contestacao_presente: bool | None = None,
        cpf: str | None = None,
        cnpj: str | None = None,
        chave: str | None = None,
        pagina_atual: int | None = None,
        itens_por_pagina: int | None = None,
    ) -> dict[str, Any]:
        """
        Consultar PIX recebidos (endpoint exclusivo BB).

        Endpoint exclusivo do Banco do Brasil para consultar PIX recebidos com filtros
        avançados não disponíveis no endpoint padrão /pix.

        Args:
            inicio: Data de início da consulta (formato ISO RFC 3339)
            fim: Data de fim da consulta (formato ISO RFC 3339)
            txid: Identificador da transação (opcional)
            txid_presente: Filtro por presença de txid (opcional)
            devolucao_presente: Filtro por presença de devolução (opcional)
            contestacao_presente: Filtro por presença de contestação (opcional)
            cpf: CPF do pagador (11 dígitos). Não pode ser usado com CNPJ
            cnpj: CNPJ do pagador (14 dígitos). Não pode ser usado com CPF
            chave: Chave DICT do recebedor (telefone, e-mail, cpf/cnpj ou EVP)
            pagina_atual: Página atual para paginação (padrão: 0)
            itens_por_pagina: Quantidade de itens por página (padrão: 100)

        Returns:
            dict contendo a lista de PIX recebidos com informações detalhadas

        Raises:
            HTTPError: Para erros 403, 404, 503
            ValueError: Se CPF e CNPJ forem informados simultaneamente
        """
        if cpf and cnpj:
            raise ValueError('CPF e CNPJ não podem ser utilizados simultaneamente')

        headers = self._create_headers()
        url = f'{self.get_base_url()}/pix-bb'
        params = self._build_pix_bb_params(
            inicio,
            fim,
            txid,
            txid_presente,
            devolucao_presente,
            contestacao_presente,
            cpf,
            cnpj,
            chave,
            pagina_atual,
            itens_por_pagina,
        )

        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp)
        return resp.json()

    def consultar_devolucoes_bb(
        self,
        inicio: str,
        fim: str,
        estado_devolucao: str | None = None,
        cpf: str | None = None,
        cnpj: str | None = None,
        pagina_atual: int | None = None,
        itens_por_pagina: int | None = None,
    ) -> dict[str, Any]:
        """
        Consultar devoluções de PIX (endpoint exclusivo BB).

        Endpoint exclusivo do Banco do Brasil para consultar devoluções de PIX
        com filtros avançados. O parâmetro data início/fim considera a data da devolução.

        Args:
            inicio: Data de início da consulta (formato ISO RFC 3339)
            fim: Data de fim da consulta (formato ISO RFC 3339)
            estado_devolucao: Estado da devolução para filtro. Valores possíveis:
                - EM_PROCESSAMENTO: Devolução em processamento
                - DEVOLVIDO: Devolução concluída com sucesso
                - NAO_REALIZADO: Devolução não realizada
                - DEVOLUCAO_MED: Devolução via MED (Mecanismo Especial de Devolução)
            cpf: CPF do pagador (11 dígitos). Não pode ser usado com CNPJ
            cnpj: CNPJ do pagador (14 dígitos). Não pode ser usado com CPF
            pagina_atual: Página atual para paginação (padrão: 0)
            itens_por_pagina: Quantidade de itens por página (padrão: 100)

        Returns:
            dict contendo a lista de devoluções com informações detalhadas

        Raises:
            HTTPError: Para erros 403, 404, 503
            ValueError: Se CPF e CNPJ forem informados simultaneamente
        """
        if cpf and cnpj:
            raise ValueError('CPF e CNPJ não podem ser utilizados simultaneamente')

        headers = self._create_headers()
        url = f'{self.get_base_url()}/pix-bb/devolucoes'
        params: dict[str, Any] = {'inicio': inicio, 'fim': fim}

        if estado_devolucao:
            params['estadoDevolucao'] = estado_devolucao
        if cpf:
            params['cpf'] = cpf
        if cnpj:
            params['cnpj'] = cnpj
        if pagina_atual is not None:
            params['paginacao.paginaAtual'] = str(pagina_atual)
        if itens_por_pagina is not None:
            params['paginacao.itensPorPagina'] = str(itens_por_pagina)

        resp = self.session.get(url, headers=headers, params=params)
        self._handle_error_response(resp)
        return resp.json()
