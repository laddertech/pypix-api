import pytest

from pypix_api.auth.oauth2 import OAuth2Client


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
