"""
pypix_api.banks.webhook_methods
-------------------------------

Este módulo implementa a classe `WebHookMethods`, que fornece métodos para operações de webhook do PIX, conforme especificação do Banco Central do Brasil.

A classe `WebHookMethods` é utilizada como base para integração com APIs bancárias que suportam o PIX, permitindo configurar webhooks para notificações de recebimento. Os métodos abstraem detalhes de requisições HTTP, tratamento de erros e montagem de parâmetros, facilitando a integração de sistemas Python com provedores bancários.

Principais funcionalidades:
- Configuração de webhook para notificações de Pix recebidos

Esta classe é herdada por implementações específicas de bancos (ex: Banco do Brasil, Sicoob).

Dependências:
- session HTTP compatível (ex: requests.Session)
- Método auxiliar: `_request()`, fornecido por `BankPixAPIBase`

Exemplo de uso:
    class MeuBanco(WebHookMethods):
        ...

    banco = MeuBanco()
    resposta = banco.configurar_webhook(chave="minha-chave", webhook_url="https://example.com/webhook/")

"""

from typing import Any


class WebHookMethods:  # pylint: disable=E1101
    """
    Classe que implementa os métodos para operações de webhook do PIX.
    Esta classe é herdada pela BankPixAPIBase.
    """

    def configurar_webhook(self, chave: str, webhook_url: str) -> dict[str, Any]:
        """
        Configurar o Webhook Pix.

        Endpoint para configuração do serviço de notificações acerca de Pix recebidos.
        Somente Pix associados a um txid serão notificados.

        Args:
            chave: Chave Pix para configuração do webhook
            webhook_url: URL do webhook para notificações (ex: "https://pix.example.com/api/webhook/")

        Returns:
            dict contendo os dados da configuração do webhook

        Raises:
            HTTPError: Para erros 400, 403, 404, 503
        """
        body = {'webhookUrl': webhook_url}
        resp = self._request('PUT', f'/webhook/{chave}', json=body)
        return self._json_opcional(resp)

    def listar_webhooks(
        self, inicio: str, fim: str, pagina_atual: int = 0, itens_por_pagina: int = 100
    ) -> dict[str, Any]:
        """
        Consultar webhooks cadastrados.

        Endpoint para consultar Webhooks Pix configurados no período especificado.

        Args:
            inicio: Data de início da consulta (formato ISO)
            fim: Data de fim da consulta (formato ISO)
            pagina_atual: Página atual para paginação (default: 0)
            itens_por_pagina: Quantidade de itens por página (default: 100)

        Returns:
            dict contendo a lista paginada de webhooks

        Raises:
            HTTPError: Para erros 403, 503
        """
        params = {
            'inicio': inicio,
            'fim': fim,
            'paginacao.paginaAtual': pagina_atual,
            'paginacao.itensPorPagina': itens_por_pagina,
        }
        resp = self._request('GET', '/webhook', params=params)
        return self._json(resp)

    def excluir_webhook(self, chave: str) -> bool:
        """
        Cancelar o Webhook Pix.

        Endpoint para cancelamento do webhook. Não é a única forma pela qual um webhook pode ser removido.
        O PSP recebedor pode remover unilateralmente um webhook associado a uma chave que não pertence mais
        a este usuário recebedor.

        Args:
            chave: Chave Pix para cancelamento do webhook

        Returns:
            bool: True se o webhook foi excluído com sucesso (status 204), False caso contrário

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        resp = self._request('DELETE', f'/webhook/{chave}')
        # `_request` já levantou em caso de erro: qualquer 2xx é exclusão
        # bem-sucedida. A especificação prevê 204, mas um PSP que responda
        # 200 não deve ser lido como "não excluiu".
        return resp.ok

    def consultar_webhook(self, chave: str) -> dict[str, Any]:
        """
        Consultar informações do Webhook Pix.

        Endpoint para recuperação de informações sobre o Webhook Pix configurado.

        Args:
            chave: Chave Pix para consulta do webhook

        Returns:
            dict contendo as informações do webhook configurado

        Raises:
            HTTPError: Para erros 403, 404, 503
        """
        resp = self._request('GET', f'/webhook/{chave}')
        return self._json(resp)
