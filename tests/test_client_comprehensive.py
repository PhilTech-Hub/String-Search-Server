import ssl

"""
COMPREHENSIVE CLIENT TESTS
Cover missing client functionality for better coverage.
"""

import pytest
import socket
from unittest.mock import patch, MagicMock
from client.client import StringSearchClient


class TestClientComprehensive:
    """Comprehensive client tests to improve coverage."""

    def test_client_initialization_variations(self):
        """Test client initialization with various parameters."""
        # Test default initialization
        client1 = StringSearchClient()
        assert client1.host == "127.0.0.1"
        assert client1.port == 44445
        assert client1.use_ssl == False

        # Test custom initialization
        client2 = StringSearchClient(host="192.168.1.1", port=8080, use_ssl=True)
        assert client2.host == "192.168.1.1"
        assert client2.port == 8080
        assert client2.use_ssl == True

        # Test with SSL parameters
        client3 = StringSearchClient(
            host="localhost",
            port=443,
            use_ssl=True,
            certfile="/path/to/cert.crt",
            keyfile="/path/to/key.key",
            cafile="/path/to/ca.crt",
            psk="secretkey",
        )
        assert client3.certfile == "/path/to/cert.crt"
        assert client3.psk == "secretkey"

    def test_connect_success(self):
        """Test successful connection scenarios."""
        client = StringSearchClient(host="127.0.0.1", port=44445, use_ssl=False)

        # Mock socket operations for successful connection
        with patch("socket.socket") as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value = mock_sock_instance

            # Mock successful connection
            mock_sock_instance.connect.return_value = None

            client.connect()

            # Verify socket was created and connected
            mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
            mock_sock_instance.settimeout.assert_called_once_with(10)
            mock_sock_instance.connect.assert_called_once_with(("127.0.0.1", 44445))

    def test_connect_ssl_success(self):
        """Test successful SSL connection."""
        client = StringSearchClient(host="127.0.0.1", port=44445, use_ssl=True)

        with patch("socket.socket") as mock_socket:
            with patch("ssl.create_default_context") as mock_ssl_context:
                mock_sock_instance = MagicMock()
                mock_socket.return_value = mock_sock_instance

                mock_ssl_context_instance = MagicMock()
                mock_ssl_context.return_value = mock_ssl_context_instance
                mock_ssl_context_instance.wrap_socket.return_value = mock_sock_instance

                client.connect()

                # Verify SSL context was created and used
                mock_ssl_context.assert_called_once_with(ssl.Purpose.SERVER_AUTH)
                mock_ssl_context_instance.wrap_socket.assert_called_once()

    def test_connect_failures(self):
        """Test various connection failure scenarios."""
        client = StringSearchClient(host="127.0.0.1", port=44445)

        # Test connection timeout
        with patch("socket.socket") as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.side_effect = socket.timeout("Connection timeout")

            with pytest.raises(ConnectionError, match="Connection timeout"):
                client.connect()

        # Test connection refused
        with patch("socket.socket") as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect.side_effect = ConnectionRefusedError("Connection refused")

            with pytest.raises(ConnectionError, match="Connection refused"):
                client.connect()

    def test_send_query_success(self):
        """Test successful query sending."""
        client = StringSearchClient()

        # Mock connected socket
        mock_socket = MagicMock()
        client.socket = mock_socket
        mock_socket.sendall.return_value = None
        mock_socket.recv.return_value = b"STRING EXISTS\n"

        result = client.send_query("test search")

        # Verify query was sent and response received
        mock_socket.sendall.assert_called_once()
        mock_socket.recv.assert_called_once_with(1024)
        assert result == "STRING EXISTS"

    def test_send_query_failures(self):
        """Test query sending failure scenarios."""
        client = StringSearchClient()

        # Test sending without connection
        with pytest.raises(ConnectionError, match="Client not connected"):
            client.send_query("test")

        # Setup connected client
        mock_socket = MagicMock()
        client.socket = mock_socket

        # Test empty query
        with pytest.raises(ValueError, match="Search query cannot be empty"):
            client.send_query("")

        # Test whitespace-only query
        with pytest.raises(ValueError, match="Search query cannot be empty"):
            client.send_query("   ")

        # Test 1: Timeout during send - should give "Server response timeout"
        mock_socket.sendall.side_effect = TimeoutError("Send timeout")
        with pytest.raises(ConnectionError, match="Server response timeout"):
            client.send_query("test")

        # Reset the mock for next test
        mock_socket.sendall.side_effect = None

        # Test 2: Connection reset during send - should give "Server connection lost"
        mock_socket.sendall.side_effect = ConnectionResetError("Connection reset during send")
        with pytest.raises(ConnectionError, match="Server connection lost"):
            client.send_query("test")

        # Reset the mock for next test
        mock_socket.sendall.side_effect = None
        mock_socket.sendall.return_value = None

        # Test 3: Connection reset during receive - should give "Server connection lost"
        mock_socket.recv.side_effect = ConnectionResetError("Connection reset during receive")
        with pytest.raises(ConnectionError, match="Server connection lost"):
            client.send_query("test")

    def test_close_operations(self):
        """Test client close operations."""
        client = StringSearchClient()

        # Test close without socket
        client.close()  # Should not raise any error

        # Test close with socket
        mock_socket = MagicMock()
        client.socket = mock_socket
        client.close()

        mock_socket.close.assert_called_once()
        assert client.socket is None

        # Test close with socket exception
        mock_socket = MagicMock()
        mock_socket.close.side_effect = Exception("Close error")
        client.socket = mock_socket
        client.close()  # Should handle exception gracefully

        assert client.socket is None

    def test_ssl_configuration_scenarios(self):
        """Test various SSL configuration scenarios."""
        # Test SSL with certificates
        client = StringSearchClient(use_ssl=True, certfile="cert.crt", keyfile="key.key")
        with patch("socket.socket"):
            with patch("ssl.create_default_context") as mock_ssl_context:
                mock_ssl_instance = MagicMock()
                mock_ssl_context.return_value = mock_ssl_instance

                with patch.object(client, "socket", MagicMock()):
                    # This will test the SSL configuration path
                    try:
                        client.connect()
                    except BaseException:
                        pass  # We're testing the configuration, not full connection

                # Verify certificate loading was attempted
                mock_ssl_instance.load_cert_chain.assert_called_once_with(
                    certfile="cert.crt", keyfile="key.key"
                )

        # Test SSL with CA file
        client = StringSearchClient(use_ssl=True, cafile="ca.crt")
        with patch("socket.socket"):
            with patch("ssl.create_default_context") as mock_ssl_context:
                mock_ssl_instance = MagicMock()
                mock_ssl_context.return_value = mock_ssl_instance

                with patch.object(client, "socket", MagicMock()):
                    try:
                        client.connect()
                    except BaseException:
                        pass

                # Verify CA file loading was attempted
                mock_ssl_instance.load_verify_locations.assert_called_once_with(cafile="ca.crt")

    def test_send_query_network_errors(self):
        """Test various network error scenarios."""
        client = StringSearchClient()
        mock_socket = MagicMock()
        client.socket = mock_socket

        # Test broken pipe error
        mock_socket.sendall.side_effect = BrokenPipeError("Broken pipe")
        with pytest.raises(ConnectionError, match="Server connection lost"):
            client.send_query("test")

        # Test generic OSError
        mock_socket.sendall.side_effect = OSError("Network unreachable")
        with pytest.raises(ConnectionError, match="Communication error with server"):
            client.send_query("test")
