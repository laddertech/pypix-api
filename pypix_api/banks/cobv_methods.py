from typing import Optional, Dict, Any
import requests


class CobVMethods:
    """
    Métodos para lidar com cobrança Pix com vencimento (CobV).
    """

    def criar_cobv(self, txid: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria uma cobrança com vencimento (CobV).
        """
        token = self.oauth.get_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        url = f'{self.BASE_URL}/cobv/{txid}'
        resp = self.session.put(url, headers=headers, json=body)
        resp.raise_for_status()
        return resp.json()

    def revisar_cobv(self, txid: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Revisa uma cobrança com vencimento (CobV).
        """
        token = self.oauth.get_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        url = f'{self.BASE_URL}/cobv/{txid}'
        resp = self.session.patch(url, headers=headers, json=body)
        resp.raise_for_status()
        return resp.json()

    def consultar_cobv(
        self, txid: str, revisao: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Consulta uma cobrança com vencimento (CobV) por txid.
        """
        token = self.oauth.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        params = {}
        if revisao is not None:
            params['revisao'] = revisao
        url = f'{self.BASE_URL}/cobv/{txid}'
        resp = self.session.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def listar_cobv(
        self,
        inicio: str,
        fim: str,
        cpf: Optional[str] = None,
        cnpj: Optional[str] = None,
        locationPresente: Optional[bool] = None,
        status: Optional[str] = None,
        loteCobVId: Optional[int] = None,
        paginaAtual: Optional[int] = None,
        itensPorPagina: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Consulta lista de cobranças com vencimento (CobV).
        """
        token = self.oauth.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        params = {'inicio': inicio, 'fim': fim}
        if cpf:
            params['cpf'] = cpf
        if cnpj:
            params['cnpj'] = cnpj
        if locationPresente is not None:
            params['locationPresente'] = str(locationPresente).lower()
        if status:
            params['status'] = status
        if loteCobVId is not None:
            params['loteCobVId'] = loteCobVId
        if paginaAtual is not None:
            params['paginaAtual'] = paginaAtual
        if itensPorPagina is not None:
            params['itensPorPagina'] = itensPorPagina

        url = f'{self.BASE_URL}/cobv'
        resp = self.session.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()
