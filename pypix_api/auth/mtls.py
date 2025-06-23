import requests

def get_session_with_mtls(cert_path: str, key_path: str) -> requests.Session:
    session = requests.Session()
    session.cert = (cert_path, key_path)
    return session
