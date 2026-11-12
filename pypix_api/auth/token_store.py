"""Armazenamento plugável de tokens OAuth2.

Por padrão, :class:`~pypix_api.auth.oauth2.OAuth2Client` guarda o token só na
memória da própria instância. Uma aplicação que cria um cliente por requisição
(o caso comum em servidores web e workers) pede, assim, um token novo ao PSP
a cada operação — e os PSPs limitam a emissão: o Sicredi responde ``429
Limite de tokens excedido`` e o Guia Técnico dele associa volume de
requisições de token a bloqueio por IP.

Um :class:`TokenStore` compartilhado (Redis, cache do framework, etc.) deixa
instâncias diferentes reaproveitarem o mesmo token enquanto ele vale.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

__all__ = ['InMemoryTokenStore', 'TokenStore']


@runtime_checkable
class TokenStore(Protocol):
    """Contrato mínimo de um armazenamento de tokens.

    As chaves já chegam isoladas por PSP, credencial e escopos (ver
    ``OAuth2Client._chave_do_store``) e não contêm segredo em claro. O valor é
    o dicionário devolvido pelo PSP acrescido de ``expires_at`` (epoch, em
    segundos) — serializável em JSON.

    Falhas do store nunca impedem a obtenção do token: o cliente registra o
    erro e segue pedindo ao PSP.
    """

    def get(self, key: str) -> dict[str, Any] | None:
        """Token guardado na chave, ou ``None`` se não houver."""
        ...

    def set(self, key: str, value: dict[str, Any], ttl: int) -> None:
        """Guarda o token por ``ttl`` segundos (já descontada a margem)."""
        ...


# Opcional: um store pode oferecer ``lock(key)``, devolvendo um context
# manager de trava distribuída (ex.: ``django_redis`` ``cache.lock``). Com
# ele, a renovação de um token vencido é serializada por chave e as demais
# instâncias esperam e reaproveitam o token novo, em vez de cada uma pedir o
# seu ao PSP. Fica fora do ``Protocol`` para não obrigar stores simples.


class InMemoryTokenStore:
    """Store em memória do processo, sem expiração própria.

    Útil para compartilhar o token entre clientes do mesmo processo. A
    validade é conferida pelo cliente via ``expires_at``.
    """

    def __init__(self) -> None:
        self._dados: dict[str, dict[str, Any]] = {}

    def get(self, key: str) -> dict[str, Any] | None:
        return self._dados.get(key)

    def set(self, key: str, value: dict[str, Any], ttl: int) -> None:
        self._dados[key] = value
