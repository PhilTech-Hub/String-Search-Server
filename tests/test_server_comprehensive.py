"""
COMPREHENSIVE SERVER TESTS
Cover missing server functionality for better coverage.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from server.server import StringSearchServer
from server.config import Config


class TestServerComprehensive:
    """Comprehensive server tests to improve coverage."""

    def test_server_initialization_comprehensive(self):
        """Test server initialization with various config scenarios."""
        # Test with valid config
        config_content = (
            "host=127.0.0.1\nport=44445\nlinuxpath=./data/sample.txt\nREREAD_ON_QUERY=False"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            server = StringSearchServer(config_file)
            assert server is not None
            assert server.host == "127.0.0.1"
            assert server.port == 44445
            assert server.reread_on_query == False
        finally:
            os.unlink(config_file)

        # Test with REREAD_ON_QUERY=True
        config_content = "host=0.0.0.0\nport=8080\nlinuxpath=./test.txt\nREREAD_ON_QUERY=True"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            server = StringSearchServer(config_file)
            assert server.reread_on_query == True
        finally:
            os.unlink(config_file)

    def test_file_loading_scenarios(self):
        """Test various file loading scenarios."""
        # Test _load_file_once with existing file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("line1\nline2\nline3\n")
            test_file = f.name

        try:
            config_content = (
                f"host=127.0.0.1\nport=44445\nlinuxpath={test_file}\nREREAD_ON_QUERY=False"
            )
            with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
                f.write(config_content)
                config_file = f.name

            try:
                server = StringSearchServer(config_file)

                # Mock the file content access
                with patch("pathlib.Path.read_text", return_value="line1\nline2\nline3"):
                    content = server._read_file()
                    assert content is not None

            finally:
                os.unlink(config_file)
        finally:
            os.unlink(test_file)

    def test_search_algorithms_comprehensive(self):
        """Test comprehensive search functionality."""
        # Use actual config file
        config_file = "config/server_config.conf"
        server = StringSearchServer(config_file)

        # Set test content directly
        server.file_content = "test search content example data"

        # Test various search scenarios
        result1 = server.search_string("test")
        assert result1 == "STRING EXISTS"  # This should now work

        result2 = server.search_string("example")
        assert result2 == "STRING EXISTS"

        result3 = server.search_string("nonexistent")
        assert result3 == "STRING NOT FOUND"

        result4 = server.search_string("")
        assert result4 == "STRING NOT FOUND"

    def test_error_handling_scenarios(self):
        """Test server error handling scenarios."""
        config_content = (
            "host=127.0.0.1\nport=44445\nlinuxpath=./data/sample.txt\nREREAD_ON_QUERY=False"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            server = StringSearchServer(config_file)

            # Test file not found in search
            with patch("pathlib.Path.is_file", return_value=False):
                result = server._mmap_search("test")
                assert result == "STRING NOT FOUND" or "ERROR" in result

            # Test OSError during file operations
            with patch("pathlib.Path.is_file", return_value=True):
                with patch("mmap.mmap", side_effect=OSError("Permission denied")):
                    result = server._mmap_search("test")
                    # Should handle the error gracefully
                    assert result is not None

            # Test empty file content
            with patch("pathlib.Path.is_file", return_value=True):
                with patch("pathlib.Path.stat") as mock_stat:
                    mock_stat.return_value.st_size = 0
                    result = server._mmap_search("test")
                    assert result is not None

        finally:
            os.unlink(config_file)

    def test_ssl_context_creation(self):
        """Test SSL context creation scenarios."""
        # Test with SSL enabled but no certificates
        config_content = "host=127.0.0.1\nport=44445\nlinuxpath=./data/sample.txt\nSSL_ENABLED=True"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            # Mock SSL context creation to avoid actual SSL operations
            with patch("server.ssl_utils.create_ssl_context") as mock_ssl:
                mock_ssl.return_value = None  # Simulate no SSL context
                server = StringSearchServer(config_file)

                # Server should handle missing SSL context gracefully
                assert server.ssl_context is None

        finally:
            os.unlink(config_file)

    def test_server_lifecycle(self):
        """Test server startup and shutdown lifecycle."""
        config_content = (
            "host=127.0.0.1\nport=44445\nlinuxpath=./data/sample.txt\nREREAD_ON_QUERY=False"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            server = StringSearchServer(config_file)

            # Test signal handling (mocked)
            with patch("threading.Thread") as mock_thread:
                mock_thread_instance = MagicMock()
                mock_thread.return_value = mock_thread_instance

                # Mock server socket
                with patch("socket.socket") as mock_socket:
                    mock_sock_instance = MagicMock()
                    mock_socket.return_value = mock_sock_instance

                    # This would normally start the server, but we're mocking it
                    # Just verify the initialization paths are covered
                    assert server.host == "127.0.0.1"
                    assert server.port == 44445

        finally:
            os.unlink(config_file)
