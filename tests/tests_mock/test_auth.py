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
