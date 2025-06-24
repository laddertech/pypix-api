"""
Test cases for the Rec methods of BankPixAPIBase.
"""

from unittest.mock import MagicMock

import pytest

from pypix_api.banks.base import BankPixAPIBase


class DummyBankPixAPIBase(BankPixAPIBase):
    """Dummy implementation of BankPixAPIBase for testing Rec methods."""

    BASE_URL = 'https://dummy'
    TOKEN_URL = 'https://dummy/token'  # noqa: S105
    SCOPES = ['dummy.scope']  # noqa: RUF012

    def __init__(self) -> None:
        # Não chama o __init__ original para evitar dependências reais
        pass

    def _create_headers(self) -> dict:
        return {
            'Authorization': 'Bearer dummy',
            'Content-Type': 'application/json',
            'client_id': 'id',
        }

    def get_base_url(self) -> str:
        return self.BASE_URL


@pytest.fixture
def dummy_bank_pix_api() -> DummyBankPixAPIBase:
    api = DummyBankPixAPIBase()
    api.session = MagicMock()
    return api


def test_criar_recorrencia(dummy_bank_pix_api) -> None:  # noqa: ANN001
    dummy_bank_pix_api.session.put.return_value = MagicMock(
        json=lambda: {'result': 'ok'}, raise_for_status=lambda: None
    )
    id_rec = 'rec123'
    body = {'valor': 500}
    result = dummy_bank_pix_api.criar_recorrencia(id_rec, body)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.put.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.put.call_args
    assert id_rec in args[0]
    assert kwargs['json'] == body


def test_revisar_recorrencia(dummy_bank_pix_api) -> None:  # noqa: ANN001
    dummy_bank_pix_api.session.patch.return_value = MagicMock(
        json=lambda: {'result': 'ok'}, raise_for_status=lambda: None
    )
    id_rec = 'rec456'
    body = {'valor': 600}
    result = dummy_bank_pix_api.revisar_recorrencia(id_rec, body)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.patch.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.patch.call_args
    assert id_rec in args[0]
    assert kwargs['json'] == body


def test_consultar_recorrencia(dummy_bank_pix_api):  # noqa: ANN001, ANN201
    dummy_bank_pix_api.session.get.return_value = MagicMock(
        json=lambda: {'result': 'ok'}, raise_for_status=lambda: None
    )
    id_rec = 'rec789'
    result = dummy_bank_pix_api.consultar_recorrencia(id_rec)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.get.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.get.call_args
    assert id_rec in args[0]
    assert 'params' in kwargs
    assert kwargs['params'] == {}


def test_consultar_recorrencia_com_txid(dummy_bank_pix_api):  # noqa: ANN001, ANN201
    dummy_bank_pix_api.session.get.return_value = MagicMock(
        json=lambda: {'result': 'ok'}, raise_for_status=lambda: None
    )
    id_rec = 'rec101'
    txid = 'txid999'
    result = dummy_bank_pix_api.consultar_recorrencia(id_rec, txid=txid)
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.get.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.get.call_args
    assert id_rec in args[0]
    assert kwargs['params']['txid'] == txid


def test_listar_recorrencias(dummy_bank_pix_api):  # noqa: ANN001, ANN201
    dummy_bank_pix_api.session.get.return_value = MagicMock(
        json=lambda: {'result': 'ok'}, raise_for_status=lambda: None
    )
    inicio = '2024-01-01T00:00:00Z'
    fim = '2024-01-31T23:59:59Z'
    result = dummy_bank_pix_api.listar_recorrencias(
        inicio,
        fim,
        cpf='12345678901',
        status='ATIVA',
        pagina_atual=1,
        itens_por_pagina=10,
    )
    assert result == {'result': 'ok'}
    dummy_bank_pix_api.session.get.assert_called_once()
    args, kwargs = dummy_bank_pix_api.session.get.call_args
    assert args[0].endswith('/rec')
    params = kwargs['params']
    assert params['inicio'] == inicio
    assert params['fim'] == fim
    assert params['cpf'] == '12345678901'
    assert params['status'] == 'ATIVA'
    assert params['paginaAtual'] == 1
    assert params['itensPorPagina'] == 10


def test_listar_recorrencias_cpf_cnpj_error(dummy_bank_pix_api) -> None:  # noqa: ANN001
    with pytest.raises(ValueError):
        dummy_bank_pix_api.listar_recorrencias(
            '2024-01-01T00:00:00Z', '2024-01-31T23:59:59Z', cpf='123', cnpj='456'
        )
