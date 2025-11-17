import unittest
from unittest.mock import patch, MagicMock
from client.client import StringSearchClient


class TestStringSearchClientFull(unittest.TestCase):
    """Full unit tests for StringSearchClient."""

    def setUp(self):
        self.host = "127.0.0.1"
        self.port = 44445

    @patch("socket.socket")
    def test_close_without_connect(self, mock_socket_class):
        client = StringSearchClient()
        client.close()
        self.assertIsNone(client.socket)

    @patch("socket.socket")
    def test_connect_and_send_query(self, mock_socket_class):
        fake_socket = MagicMock()
        fake_socket.recv.return_value = b"STRING EXISTS\n"
        mock_socket_class.return_value = fake_socket

        client = StringSearchClient(host=self.host, port=self.port, use_ssl=False)
        client.connect()
        mock_socket_class.return_value.connect.assert_called_with((self.host, self.port))

        response = client.send_query("line1")
        self.assertEqual(response, "STRING EXISTS")
        fake_socket.sendall.assert_called_with(b"line1\n")

        client.close()
        self.assertIsNone(client.socket)

    @patch("socket.socket")
    def test_connection_logging(self, mock_socket_class):
        fake_socket = MagicMock()
        fake_socket.recv.return_value = b"STRING EXISTS\n"
        mock_socket_class.return_value = fake_socket

        from io import StringIO
        import sys

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            client = StringSearchClient(host=self.host, port=self.port, use_ssl=False)
            client.connect()
            client.send_query("test")
            client.close()

            logs = sys.stdout.getvalue()
            self.assertIn("Establishing plain text connection", logs)
            self.assertIn("Successfully connected", logs)
        finally:
            sys.stdout = old_stdout

    @patch("socket.socket")
    def test_send_query_empty_string(self, mock_socket_class):
        fake_socket = MagicMock()
        fake_socket.recv.return_value = b"STRING NOT FOUND\n"
        mock_socket_class.return_value = fake_socket

        # Mock SSL context to avoid real SSL operations
        with patch("ssl.create_default_context") as mock_ssl_context:
            mock_context = MagicMock()
            mock_ssl_context.return_value = mock_context
            mock_ssl_socket = MagicMock()
            mock_context.wrap_socket.return_value = mock_ssl_socket

            client = StringSearchClient(host=self.host, port=self.port, use_ssl=False)
            client.connect()

            # Empty query should now raise ValueError
            with self.assertRaises(ValueError) as context:
                client.send_query("")
            self.assertIn("Search query cannot be empty", str(context.exception))

            client.close()

    @patch("socket.socket")
    def test_send_query_non_utf8(self, mock_socket_class):
        fake_socket = MagicMock()
        fake_socket.recv.return_value = b"STRING NOT FOUND\n"
        mock_socket_class.return_value = fake_socket

        # Mock SSL context to avoid real SSL operations
        with patch("ssl.create_default_context") as mock_ssl_context:
            mock_context = MagicMock()
            mock_ssl_context.return_value = mock_context
            mock_ssl_socket = MagicMock()
            mock_context.wrap_socket.return_value = mock_ssl_socket

            client = StringSearchClient(host=self.host, port=self.port, use_ssl=False)
            client.connect()
            response = client.send_query("café")
            self.assertEqual(response, "STRING NOT FOUND")
            client.close()

    @patch("socket.socket")
    @patch("ssl.SSLContext.wrap_socket")
    def test_ssl_connection(self, mock_wrap_socket, mock_socket_class):
        fake_socket = MagicMock()
        mock_socket_class.return_value = fake_socket
        mock_wrap_socket.return_value = fake_socket

        client = StringSearchClient(host=self.host, port=self.port, use_ssl=True)
        client.connect()
        mock_wrap_socket.assert_called_once()
        client.close()

    @patch("socket.socket")
    @patch("ssl.SSLContext.wrap_socket")
    def test_ssl_connection_logging(self, mock_wrap_socket, mock_socket_class):
        fake_socket = MagicMock()
        mock_socket_class.return_value = fake_socket
        mock_wrap_socket.return_value = fake_socket

        from io import StringIO
        import sys

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            client = StringSearchClient(host=self.host, port=self.port, use_ssl=True)
            client.connect()
            client.close()

            logs = sys.stdout.getvalue()
            self.assertIn("Establishing secure SSL/TLS connection", logs)
            self.assertIn("SSL/TLS: Yes", logs)
        finally:
            sys.stdout = old_stdout


if __name__ == "__main__":
    unittest.main()
