# tests/test_server_remaining.py
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from server.server import StringSearchServer


class TestServerRemainingCoverage(unittest.TestCase):
    """Test cases for remaining server functionality to achieve full coverage."""

    def test_mmap_search_file_not_found(self):
        """Test mmap search when file doesn't exist."""
        config_content = (
            "host=127.0.0.1\nport=44445\nlinuxpath=./nonexistent.txt\nREREAD_ON_QUERY=False"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            server = StringSearchServer(config_file)

            # File doesn't exist, should return appropriate message
            result = server._mmap_search("test")
            # FIXED: Expect string result, not boolean
            assert result == "STRING NOT FOUND"
            assert isinstance(result, str)  # Should be string, not bool
        finally:
            import os

            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_search_string_exception_handling(self):
        """Test that search_string handles exceptions properly and returns string results."""
        # Use the actual config file
        config_file = "config/server_config.conf"
        server = StringSearchServer(config_file)

        # Test with invalid file content
        server.file_content = None
        result = server.search_string("test")

        # FIXED: Should return string, not boolean
        assert result == "STRING NOT FOUND"
        assert isinstance(result, str)  # Changed from bool to str

        # Test with empty file content
        server.file_content = ""
        result = server.search_string("test")
        assert result == "STRING NOT FOUND"
        assert isinstance(result, str)  # Changed from bool to str

    def test_ssl_context_creation_failure(self):
        """Test SSL context creation failure handling."""
        config_content = """host=127.0.0.1
port=44445
linuxpath=./data/sample_text.txt
REREAD_ON_QUERY=False
SSL_ENABLED=True
ssl_cert_file=/nonexistent/cert.pem
ssl_key_file=/nonexistent/key.pem
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            # Should handle SSL failure gracefully
            server = StringSearchServer(config_file)
            # Server should still be created even if SSL fails
            self.assertIsNotNone(server)
            # SSL should be disabled after failure
            self.assertFalse(server.ssl_enabled)
        finally:
            import os

            if os.path.exists(config_file):
                os.unlink(config_file)


if __name__ == "__main__":
    unittest.main()
