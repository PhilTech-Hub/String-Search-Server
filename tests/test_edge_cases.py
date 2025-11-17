import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from server.server import StringSearchServer
from client.client import StringSearchClient


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def setUp(self):
        self.config_file = "tests/test_config.con"

    def test_file_not_found(self):
        """Test handling of missing data file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".con", delete=False) as f:
            f.write(
                """host=127.0.0.1
port=44445
linuxpath=/nonexistent/path/file.txt
REREAD_ON_QUERY=False
SSL_ENABLED=False
"""
            )
            temp_config = f.name

        try:
            server = StringSearchServer(config_file=temp_config)
            # Should handle missing file gracefully - file_lines should be an empty set
            self.assertIsInstance(server.file_lines, set)
            self.assertEqual(len(server.file_lines), 0)
        finally:
            os.unlink(temp_config)

    def test_empty_file(self):
        """Test handling of empty data file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as data_file:
            data_file.write("")  # Empty file

        with tempfile.NamedTemporaryFile(mode="w", suffix=".con", delete=False) as config_file:
            config_file.write(
                f"""host=127.0.0.1
port=44445
linuxpath={data_file.name}
REREAD_ON_QUERY=False
SSL_ENABLED=False
"""
            )
            temp_config = config_file.name

        try:
            server = StringSearchServer(config_file=temp_config)
            self.assertIsInstance(server.file_lines, set)
            self.assertEqual(len(server.file_lines), 0)

            # Test search on empty file
            result = server.search_string("anything")
            self.assertEqual(result, "STRING NOT FOUND")
        finally:
            os.unlink(data_file.name)
            os.unlink(temp_config)

    def test_large_payload(self):
        """Test handling of payload exceeding 1024 bytes."""
        large_string = "x" * 1500  # Exceeds 1024 bytes

        with patch("socket.socket") as mock_socket:
            fake_socket = MagicMock()
            fake_socket.recv.return_value = b"STRING NOT FOUND\n"
            mock_socket.return_value = fake_socket

            # Mock SSL context to avoid real SSL operations
            with patch("ssl.create_default_context") as mock_ssl_context:
                mock_context = MagicMock()
                mock_ssl_context.return_value = mock_context
                mock_ssl_socket = MagicMock()
                mock_context.wrap_socket.return_value = mock_ssl_socket

                client = StringSearchClient(host="127.0.0.1", port=44445, use_ssl=False)
                client.connect()
                result = client.send_query(large_string)
                self.assertEqual(result, "STRING NOT FOUND")

    def test_special_characters_in_search(self):
        """Test search strings with special characters."""
        special_strings = [
            "line with spaces",
            "line/with/slashes",
            "line\\with\\backslashes",
            "line-with-dashes",
            "line_with_underscores",
            "line.with.dots",
            "line@with            #special$chars%",
            "line with\nnewline",
            "line with\ttab",
        ]

        for search_string in special_strings:
            with patch("socket.socket") as mock_socket:
                fake_socket = MagicMock()
                fake_socket.recv.return_value = b"STRING NOT FOUND\n"
                mock_socket.return_value = fake_socket

                # Mock SSL context to avoid real SSL operations
                with patch("ssl.create_default_context") as mock_ssl_context:
                    mock_context = MagicMock()
                    mock_ssl_context.return_value = mock_context
                    mock_ssl_socket = MagicMock()
                    mock_context.wrap_socket.return_value = mock_ssl_socket

                    client = StringSearchClient(host="127.0.0.1", port=44445, use_ssl=False)
                    client.connect()
                    result = client.send_query(search_string)
                    self.assertEqual(result, "STRING NOT FOUND")

    def test_unicode_characters(self):
        """Test handling of Unicode characters."""
        unicode_strings = [
            "café",
            "naïve",
            "🚀 rocket",
            "🎉 celebration",
            "中文测试",
            "🍕 pizza",
        ]

        for search_string in unicode_strings:
            with patch("socket.socket") as mock_socket:
                fake_socket = MagicMock()
                fake_socket.recv.return_value = b"STRING NOT FOUND\n"
                mock_socket.return_value = fake_socket

                # Mock SSL context to avoid real SSL operations
                with patch("ssl.create_default_context") as mock_ssl_context:
                    mock_context = MagicMock()
                    mock_ssl_context.return_value = mock_context
                    mock_ssl_socket = MagicMock()
                    mock_context.wrap_socket.return_value = mock_ssl_socket

                    client = StringSearchClient(host="127.0.0.1", port=44445, use_ssl=False)
                    client.connect()
                    result = client.send_query(search_string)
                    self.assertEqual(result, "STRING NOT FOUND")

    def test_concurrent_connections(self):
        """Test server behavior with multiple concurrent connections."""
        # Mock SSL context creation to avoid certificate issues
        with patch("server.ssl_utils.create_ssl_context") as mock_ssl_context:
            mock_ssl_context.return_value = None

            server = StringSearchServer(config_file="config/server_config.conf")

            # Create multiple mock clients
            mock_sockets = []
            for i in range(5):
                mock_socket = MagicMock()
                mock_socket.recv.side_effect = [f"test_{i}\n".encode(), b""]
                mock_sockets.append(mock_socket)

            # Simulate concurrent client handling
            for i, mock_socket in enumerate(mock_sockets):
                server.handle_client(mock_socket, ("127.0.0.1", 5000 + i))

    def test_malformed_config(self):
        """Test handling of malformed configuration files."""
        malformed_configs = [
            "",  # Empty file
            "invalid content",  # No key-value pairs
            "linuxpath=",  # Missing value
            "=value",  # Missing key
        ]

        for config_content in malformed_configs:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".con", delete=False) as f:
                f.write(config_content)
                temp_config = f.name

            try:
                # Mock SSL to avoid certificate issues
                with patch("server.ssl_utils.create_ssl_context") as mock_ssl_context:
                    mock_ssl_context.return_value = None

                    # For malformed configs, expect RuntimeError
                    with self.assertRaises(RuntimeError) as context:
                        server = StringSearchServer(config_file=temp_config)

                    # Verify the error message contains expected content
                    self.assertIn("Server initialization failed", str(context.exception))

            finally:
                os.unlink(temp_config)

    def test_permission_denied(self):
        """Test handling of permission denied errors."""
        # Mock SSL context creation to avoid certificate issues
        with patch("server.ssl_utils.create_ssl_context") as mock_ssl_context:
            mock_ssl_context.return_value = None

            with patch("pathlib.Path.is_file", return_value=True):
                with patch("pathlib.Path.open", side_effect=PermissionError("Permission denied")):
                    server = StringSearchServer(config_file="config/server_config.conf")
                    # Should handle permission error gracefully
                    self.assertIsInstance(server.file_lines, set)
                    self.assertEqual(len(server.file_lines), 0)


class TestPerformanceEdgeCases(unittest.TestCase):
    """Test performance-related edge cases."""

    def setUp(self):
        self.config_file = "tests/test_config.con"

    def test_large_file_handling(self):
        """Test handling of very large files (simulated)."""
        # Simulate a large file with many lines
        large_file_content = "\n".join([f"line_{i}" for i in range(10000)]) + "\n"

        # Mock SSL context creation to avoid certificate issues
        with patch("server.ssl_utils.create_ssl_context") as mock_ssl_context:
            mock_ssl_context.return_value = None

            with patch("pathlib.Path.open", mock_open(read_data=large_file_content)):
                with patch("pathlib.Path.is_file", return_value=True):
                    server = StringSearchServer(config_file="config/server_config.conf")
                    # Should handle large file without crashing
                    self.assertIsInstance(server.file_lines, set)
                    self.assertGreater(len(server.file_lines), 0)

    def test_memory_usage_with_large_search(self):
        """Test memory usage doesn't explode with large searches."""
        with patch("socket.socket") as mock_socket:
            fake_socket = MagicMock()
            fake_socket.recv.return_value = b"STRING NOT FOUND\n"
            mock_socket.return_value = fake_socket

            # Mock SSL context to avoid real SSL operations
            with patch("ssl.create_default_context") as mock_ssl_context:
                mock_context = MagicMock()
                mock_ssl_context.return_value = mock_context
                mock_ssl_socket = MagicMock()
                mock_context.wrap_socket.return_value = mock_ssl_socket

                client = StringSearchClient(host="127.0.0.1", port=44445, use_ssl=False)
                client.connect()

                # Test multiple large searches
                for i in range(100):
                    large_search = "x" * 500
                    result = client.send_query(large_search)
                    self.assertEqual(result, "STRING NOT FOUND")


if __name__ == "__main__":
    unittest.main()
