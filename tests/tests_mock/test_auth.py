import pytest
import requests

from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.exceptions import (
    PixAcessoNegadoException,
    PixAPIException,
    PixConexaoException,
    PixErroDesconhecidoException,
    PixErroServicoIndisponivelException,
    PixErroServidorException,
    PixErroValidacaoException,
    PixNaoAutorizadoException,
    PixRespostaInvalidaError,
    PixTimeoutException,
)
from pypix_api.http import DEFAULT_TIMEOUT
from tests.conftest import make_response


def test_oauth2client_init(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummySession:
        pass

    monkeypatch.setattr(
        'pypix_api.auth.oauth2.get_session_with_mtls', lambda *a, **kw: DummySession()
    )
    client = OAuth2Client(
        token_url='token_url',
        client_id='client_id',
        cert='cert_path',
        pvk='key_path',
        cert_pfx='cert.pfx',
        pwd_pfx='senha',
        sandbox_mode=False,
    )
    assert client.client_id == 'client_id'
    assert client.cert == 'cert_path'
    assert client.pvk == 'key_path'
    assert client.cert_pfx == 'cert.pfx'
    assert client.pwd_pfx == 'senha'
    assert client.token_url == 'token_url'
    assert client.sandbox_mode is False
    assert isinstance(client.session, DummySession)


def test_oauth2client_assinatura_posicional_retrocompativel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A ordem posicional histórica (token_url, client_id, cert, pvk, ...) deve
    permanecer válida após a adição de client_secret ao final da assinatura."""

    class DummySession:
        pass

    monkeypatch.setattr(
        'pypix_api.auth.oauth2.get_session_with_mtls', lambda *a, **kw: DummySession()
    )
    monkeypatch.delenv('CLIENT_SECRET', raising=False)
    # Chamada posicional no formato anterior à introdução de client_secret
    client = OAuth2Client('token_url', 'cid', 'cert.pem', 'key.pem')
    assert client.client_id == 'cid'
    assert client.cert == 'cert.pem'
    assert client.pvk == 'key.pem'
    # client_secret não deve ser preenchido por deslocamento posicional
    assert client.client_secret is None


def _client_sandbox(**kwargs) -> OAuth2Client:
    return OAuth2Client(
        token_url='https://psp.exemplo/oauth/token',
        client_id='id',
        sandbox_mode=True,
        **kwargs,
    )


def test_requisicao_de_token_leva_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client_sandbox()
    capturado: dict = {}

    def fake_post(url, data=None, headers=None, timeout=None):  # type: ignore[no-untyped-def]
        capturado['timeout'] = timeout
        return make_response(200, {'access_token': 'tok', 'expires_in': 3600})

    client.session.post = fake_post  # type: ignore[method-assign]
    client.get_token('cob.read')

    assert capturado['timeout'] == DEFAULT_TIMEOUT


def test_timeout_do_construtor_vale_para_o_token() -> None:
    client = _client_sandbox(timeout=(2.0, 4.0))
    capturado: dict = {}

    def fake_post(url, data=None, headers=None, timeout=None):  # type: ignore[no-untyped-def]
        capturado['timeout'] = timeout
        return make_response(200, {'access_token': 'tok', 'expires_in': 3600})

    client.session.post = fake_post  # type: ignore[method-assign]
    client.get_token('cob.read')

    assert capturado['timeout'] == (2.0, 4.0)


def test_timeout_na_requisicao_de_token_vira_excecao_da_biblioteca() -> None:
    client = _client_sandbox()

    def fake_post(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise requests.Timeout('read timed out')

    client.session.post = fake_post  # type: ignore[method-assign]

    with pytest.raises(PixTimeoutException) as exc_info:
        client.get_token('cob.read')

    assert exc_info.value.status is None


def test_falha_de_conexao_na_requisicao_de_token() -> None:
    client = _client_sandbox()

    def fake_post(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise requests.ConnectionError('conexão recusada')

    client.session.post = fake_post  # type: ignore[method-assign]

    with pytest.raises(PixConexaoException):
        client.get_token('cob.read')


def _responde_token(client: OAuth2Client, resposta: requests.Response) -> None:
    client.session.post = lambda *a, **k: resposta  # type: ignore[method-assign]


@pytest.mark.parametrize(
    ('status', 'excecao'),
    [
        (400, PixErroValidacaoException),
        (401, PixNaoAutorizadoException),
        (403, PixAcessoNegadoException),
        (500, PixErroServidorException),
        (503, PixErroServicoIndisponivelException),
    ],
)
def test_erro_http_no_token_vira_excecao_da_biblioteca(status, excecao) -> None:
    """O endpoint de token é percorrido antes de toda operação autenticada: um
    erro dele precisa ser capturável pelo mesmo except das chamadas de negócio."""
    client = _client_sandbox()
    _responde_token(
        client,
        make_response(
            status,
            {'error': 'invalid_client', 'error_description': 'credencial recusada'},
        ),
    )

    with pytest.raises(excecao) as exc_info:
        client.get_token('cob.read')

    assert exc_info.value.status == status
    assert isinstance(exc_info.value, PixAPIException)
    # O corpo da RFC 6749 é preservado para diagnóstico
    assert 'invalid_client' in exc_info.value.detail
    assert 'credencial recusada' in exc_info.value.detail


def test_erro_no_token_sem_corpo_json_preserva_o_texto() -> None:
    client = _client_sandbox()
    _responde_token(
        client,
        make_response(
            502, content=b'<html>502 Bad Gateway</html>', content_type='text/html'
        ),
    )

    with pytest.raises(PixErroDesconhecidoException) as exc_info:
        client.get_token('cob.read')

    assert 'Bad Gateway' in exc_info.value.detail


def test_erro_no_token_nao_alimenta_o_cache() -> None:
    client = _client_sandbox()
    _responde_token(client, make_response(401, {'error': 'invalid_client'}))

    with pytest.raises(PixNaoAutorizadoException):
        client.get_token('cob.read')

    assert client.token_cache == {}


@pytest.mark.parametrize(
    ('corpo', 'content_type'),
    [
        (b'', ''),
        (b'{}', 'application/json'),
        (b'{"access_token": "tok"}', 'application/json'),
        (b'null', 'application/json'),
        (b'{"access_token": "tok", "expires_in": "abc"}', 'application/json'),
        (b'{"access_token": null, "expires_in": 3600}', 'application/json'),
    ],
    ids=[
        'vazio',
        'objeto-vazio',
        'sem-expires_in',
        'null',
        'expires_in-invalido',
        'access_token-nulo',
    ],
)
def test_resposta_de_token_incompleta_vira_resposta_invalida(
    corpo: bytes, content_type: str
) -> None:
    """200 sem access_token/expires_in estourava JSONDecodeError ou KeyError no
    meio da chamada de negócio."""
    client = _client_sandbox()
    _responde_token(
        client, make_response(200, content=corpo, content_type=content_type)
    )

    with pytest.raises(PixRespostaInvalidaError):
        client.get_token('cob.read')


def test_expires_in_como_string_e_convertido() -> None:
    """PSPs enviam expires_in como string; sem coerção, a soma com time.time()
    estourava TypeError fora da hierarquia da biblioteca."""
    client = _client_sandbox()
    _responde_token(
        client, make_response(200, {'access_token': 'tok', 'expires_in': '3600'})
    )

    assert client.get_token('cob.read') == 'tok'
    assert client.token_cache['cob.read']['expires_in'] == 3600
