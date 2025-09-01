"""
Performance benchmarks for OAuth2 authentication components.

These benchmarks measure the performance of critical authentication paths
to ensure they meet performance requirements for production use.
"""

import time
from unittest.mock import Mock, patch

import pytest

from pypix_api.auth.oauth2 import OAuth2Client


class TestOAuth2Performance:
    """Benchmarks for OAuth2 client performance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client_id = 'test-client-id'
        self.client_secret = 'test-client-secret'
        self.cert_path = '/fake/cert.p12'
        self.cert_password = 'fake-password'
        self.scope = 'test-scope'

    @pytest.mark.benchmark(group='oauth-init')
    def test_oauth_client_initialization_performance(self, benchmark):
        """Benchmark OAuth2Client initialization time."""

        def create_client():
            return OAuth2Client(
                client_id=self.client_id,
                client_secret=self.client_secret,
                cert_path=self.cert_path,
                cert_password=self.cert_password,
                scope=self.scope,
            )

        result = benchmark(create_client)
        assert result.client_id == self.client_id
        assert result.scope == self.scope

    @pytest.mark.benchmark(group='oauth-token')
    @patch('pypix_api.auth.oauth2.requests.Session.post')
    def test_token_request_performance(self, mock_post, benchmark):
        """Benchmark token request processing time."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'test-token-123',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'scope': 'test-scope',
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = OAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            cert_path=self.cert_path,
            cert_password=self.cert_password,
            scope=self.scope,
        )

        def get_token():
            return client.get_token()

        token = benchmark(get_token)
        assert token == 'test-token-123'

    @pytest.mark.benchmark(group='oauth-concurrent')
    @patch('pypix_api.auth.oauth2.requests.Session.post')
    def test_concurrent_token_requests_performance(self, mock_post, benchmark):
        """Benchmark concurrent token request handling."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'concurrent-token-123',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'scope': 'test-scope',
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = OAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            cert_path=self.cert_path,
            cert_password=self.cert_password,
            scope=self.scope,
        )

        def concurrent_requests():
            # Simulate multiple concurrent requests
            tokens = []
            for _ in range(5):
                tokens.append(client.get_token())
            return tokens

        tokens = benchmark(concurrent_requests)
        assert len(tokens) == 5
        assert all(token == 'concurrent-token-123' for token in tokens)

    @pytest.mark.benchmark(group='oauth-cache')
    @patch('pypix_api.auth.oauth2.requests.Session.post')
    def test_token_caching_performance(self, mock_post, benchmark):
        """Benchmark token caching mechanism performance."""
        call_count = 0

        def mock_post_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_response = Mock()
            mock_response.json.return_value = {
                'access_token': f'cached-token-{call_count}',
                'token_type': 'Bearer',
                'expires_in': 3600,
                'scope': 'test-scope',
            }
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            return mock_response

        mock_post.side_effect = mock_post_side_effect

        client = OAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            cert_path=self.cert_path,
            cert_password=self.cert_password,
            scope=self.scope,
        )

        def test_caching():
            # Multiple calls should use cached token
            tokens = []
            for _ in range(10):
                tokens.append(client.get_token())
            return tokens

        tokens = benchmark(test_caching)
        # Should have called the API only once due to caching
        assert call_count == 1
        assert len(set(tokens)) == 1  # All tokens should be the same


class TestOAuth2MemoryUsage:
    """Memory usage benchmarks for OAuth2 components."""

    @pytest.mark.benchmark(group='oauth-memory')
    def test_oauth_client_memory_usage(self, benchmark):
        """Benchmark memory usage of OAuth2Client."""
        import os

        import psutil

        def create_and_measure():
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss

            # Create multiple clients to test memory usage
            clients = []
            for i in range(100):
                client = OAuth2Client(
                    client_id=f'client-{i}',
                    client_secret=f'secret-{i}',
                    cert_path='/fake/cert.p12',
                    cert_password='password',
                    scope='scope',
                )
                clients.append(client)

            final_memory = process.memory_info().rss
            memory_diff = final_memory - initial_memory

            return memory_diff, len(clients)

        memory_diff, client_count = benchmark(create_and_measure)

        # Memory usage should be reasonable (less than 10MB for 100 clients)
        assert memory_diff < 10 * 1024 * 1024  # 10MB
        assert client_count == 100


class TestOAuth2ScalabilityBenchmarks:
    """Scalability benchmarks for OAuth2 operations."""

    @pytest.mark.benchmark(group='oauth-scale')
    @patch('pypix_api.auth.oauth2.requests.Session.post')
    def test_large_scope_handling_performance(self, mock_post, benchmark):
        """Benchmark handling of large scope strings."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'large-scope-token',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'scope': 'large-scope',
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Create a very large scope string
        large_scope = ' '.join([f'scope{i}' for i in range(1000)])

        def create_client_with_large_scope():
            return OAuth2Client(
                client_id='test-client',
                client_secret='test-secret',
                cert_path='/fake/cert.p12',
                cert_password='password',
                scope=large_scope,
            )

        client = benchmark(create_client_with_large_scope)
        assert len(client.scope.split()) == 1000

    @pytest.mark.benchmark(group='oauth-stress')
    @patch('pypix_api.auth.oauth2.requests.Session.post')
    def test_rapid_token_requests_performance(self, mock_post, benchmark):
        """Benchmark rapid consecutive token requests."""

        # Setup mock response with delay to simulate network
        def mock_post_with_delay(*args, **kwargs):
            time.sleep(0.001)  # 1ms delay
            mock_response = Mock()
            mock_response.json.return_value = {
                'access_token': 'rapid-token-123',
                'token_type': 'Bearer',
                'expires_in': 3600,
                'scope': 'test-scope',
            }
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            return mock_response

        mock_post.side_effect = mock_post_with_delay

        client = OAuth2Client(
            client_id='stress-test-client',
            client_secret='stress-test-secret',
            cert_path='/fake/cert.p12',
            cert_password='password',
            scope='test-scope',
        )

        def rapid_requests():
            # Clear any cached token to force new requests
            client._token = None
            client._token_expires_at = 0

            tokens = []
            for _ in range(50):
                client._token = None  # Force new request each time
                client._token_expires_at = 0
                tokens.append(client.get_token())
            return tokens

        tokens = benchmark(rapid_requests)
        assert len(tokens) == 50
        assert all(token == 'rapid-token-123' for token in tokens)
