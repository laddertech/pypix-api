Models
======

.. note::

   Os métodos das APIs de banco enviam e retornam ``dict`` cru (payloads PIX conforme a
   especificação do BACEN). ``PixCobranca`` é um modelo auxiliar mínimo e não é usado pelos
   métodos de cobrança/consulta.

PIX Models
----------

.. automodule:: pypix_api.models.pix
   :members:
   :undoc-members:
   :show-inheritance:

Status Enums
------------

Valores de status definidos pela especificação do BACEN, válidos para todos os
PSPs. Veja :doc:`../examples/pix_automatico` para o uso no cancelamento de
cobranças recorrentes.

.. automodule:: pypix_api.models.enums
   :members:
   :undoc-members:
   :show-inheritance:
