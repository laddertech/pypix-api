"""Configurações comuns das requisições HTTP da biblioteca."""

import requests

#: Quantos caracteres do corpo cru são preservados em `detail`.
LIMITE_CORPO_CRU = 500


def texto_do_corpo(response: requests.Response, limite: int = LIMITE_CORPO_CRU) -> str:
    """Decodifica o corpo da resposta preservando a acentuação.

    ``response.text`` só conhece o encoding quando o ``Content-Type`` traz
    ``charset``; sem ele, o ``requests`` adivinha e costuma errar em corpos
    curtos, transformando "inválida" em "inv√°lida" no log. JSON é UTF-8 por
    definição (RFC 8259), então é o palpite certo quando o PSP não declara.
    """
    if response.encoding:
        return response.text[:limite]
    return response.content[:limite].decode('utf-8', errors='replace')


#: Tipo aceito no parâmetro ``timeout``, igual ao do ``requests``: um número
#: aplicado a conexão e leitura, ou a tupla ``(conexão, leitura)``. ``None`` na
#: posição de leitura significa espera sem limite.
Timeout = float | tuple[float, float] | tuple[float, None]

#: Tempo limite padrão: (conexão, leitura), em segundos.
#:
#: O ``requests`` não define timeout algum por padrão — sem isto, uma resposta
#: que nunca chega prende o processo indefinidamente, sem log nem métrica.
DEFAULT_TIMEOUT: tuple[float, float] = (5.0, 30.0)
