"""Testes simplificados para o módulo de logging."""

import logging
from unittest.mock import Mock, patch

from pypix_api.logging import (
    APICallLogger,
    PIXLogger,
    StructuredFormatter,
    log_authentication,
)


class TestPIXLogger:
    """Testa a classe PIXLogger."""

    def test_pix_logger_creation(self):
        """Testa criação do logger."""
        logger = PIXLogger('test.module')
        assert logger is not None

    def test_pix_logger_info(self, caplog):
        """Testa log de info."""
        logger = PIXLogger('test')
        with caplog.at_level(logging.INFO):
            logger.info('Test message')

        assert 'Test message' in caplog.text

    def test_pix_logger_warning(self, caplog):
        """Testa log de warning."""
        logger = PIXLogger('test')
        with caplog.at_level(logging.WARNING):
            logger.warning('Warning message')

        assert 'Warning message' in caplog.text

    def test_pix_logger_error(self, caplog):
        """Testa log de erro."""
        logger = PIXLogger('test')
        with caplog.at_level(logging.ERROR):
            logger.error('Error message')

        assert 'Error message' in caplog.text


class TestStructuredFormatter:
    """Testa o StructuredFormatter."""

    def test_structured_formatter_creation(self):
        """Testa criação do formatter."""
        formatter = StructuredFormatter()
        assert formatter is not None

    def test_structured_formatter_format(self):
        """Testa formatação básica."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        assert isinstance(formatted, str)
        assert 'Test message' in formatted


class TestAPICallLogger:
    """Testa o APICallLogger."""

    def test_api_call_logger_creation(self):
        """Testa criação do APICallLogger."""
        api_logger = APICallLogger('BB')
        assert api_logger is not None


class TestLogAuthentication:
    """Testa a função log_authentication."""

    @patch('pypix_api.logging.PIXLogger')
    def test_log_authentication_success(self, mock_logger):
        """Testa log de autenticação bem-sucedida."""
        mock_instance = Mock()
        mock_logger.return_value = mock_instance

        log_authentication(client_id='client123', scope='cob.write', success=True)

        assert mock_instance.info.called

    @patch('pypix_api.logging.PIXLogger')
    def test_log_authentication_failure(self, mock_logger):
        """Testa log de falha de autenticação."""
        mock_instance = Mock()
        mock_logger.return_value = mock_instance

        log_authentication(client_id='client123', scope='cob.write', success=False)

        assert mock_instance.warning.called
