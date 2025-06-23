import requests

def get(url, headers=None, cert=None):
    return requests.get(url, headers=headers, cert=cert)
