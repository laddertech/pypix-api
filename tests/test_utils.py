import pytest
from pypix_api.utils.http_client import get

def test_get(monkeypatch):
    class DummyResponse:
        def __init__(self):
            self.status_code = 200
            self.text = "ok"
        def json(self):
            return {"result": "ok"}
    def dummy_requests_get(url, headers=None, cert=None):
        assert url == "http://test"
        assert headers == {"Authorization": "Bearer token"}
        assert cert == "cert.pem"
        return DummyResponse()
    monkeypatch.setattr("requests.get", dummy_requests_get)
    response = get("http://test", headers={"Authorization": "Bearer token"}, cert="cert.pem")
    assert response.status_code == 200
    assert response.text == "ok"
    assert response.json() == {"result": "ok"}
