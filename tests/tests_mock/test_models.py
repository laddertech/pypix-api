from pypix_api.models.pix import PixCobranca


def test_pix_cobranca_init() -> None:
    cobranca = PixCobranca(
        txid='abc123', valor=100.0, status='ATIVA', chave='minha-chave'
    )
    assert cobranca.txid == 'abc123'
    assert cobranca.valor == 100.0
    assert cobranca.status == 'ATIVA'
