"""
Targeted tests for remaining uncovered client lines.
"""

import pytest
from unittest.mock import patch, MagicMock
from client.client import StringSearchClient


class TestClientRemainingCoverage:
    """Tests for remaining uncovered client code."""

    def test_connect_ssl_fallback(self):
        """Test SSL connection fallback to plain socket."""
        client = StringSearchClient(host="127.0.0.1", port=44445, use_ssl=True)

        with patch("socket.socket") as mock_socket:
            with patch("ssl.create_default_context") as mock_ssl_context:
                mock_sock_instance = MagicMock()
                mock_socket.return_value = mock_sock_instance

                # Mock SSL setup failure
                mock_ssl_context.side_effect = Exception("SSL setup failed")

                client.connect()

                # Should fall back to plain socket
                assert client.use_ssl == False

    def test_send_query_connection_closed(self):
        """Test handling of closed connection during send."""
        client = StringSearchClient()
        mock_socket = MagicMock()
        client.socket = mock_socket

        # Mock server closing connection
        mock_socket.recv.return_value = b""  # Empty response

        with pytest.raises(ConnectionError, match="Server closed connection unexpectedly"):
            client.send_query("test")

    def test_close_with_exception(self):
        """Test close method with socket exception."""
        client = StringSearchClient()
        mock_socket = MagicMock()
        client.socket = mock_socket

        # Mock socket close exception
        mock_socket.close.side_effect = Exception("Close error")

        # Should handle exception gracefully
        client.close()
        assert client.socket is None
