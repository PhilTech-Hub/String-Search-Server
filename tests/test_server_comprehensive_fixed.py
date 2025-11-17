"""
FIXED Server comprehensive tests with proper return value handling.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from server.server import StringSearchServer
from server.config import Config


class TestServerComprehensiveFixed:
    """Fixed comprehensive server tests with proper return value handling."""

    def test_search_algorithms_comprehensive_fixed(self):
        """Test all search algorithms with proper return value handling."""
        config_content = (
            "host=127.0.0.1\nport=44445\nlinuxpath=./data/sample.txt\nREREAD_ON_QUERY=False"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            server = StringSearchServer(config_file)

            # Test _mmap_search with various scenarios
            with patch("pathlib.Path.is_file", return_value=True):
                with patch("mmap.mmap") as mock_mmap:
                    # Mock successful search
                    mock_mm = MagicMock()
                    mock_mm.__enter__ = MagicMock(return_value=mock_mm)
                    mock_mm.__exit__ = MagicMock(return_value=None)
                    mock_mm.find.return_value = 0
                    mock_mm.readline.return_value = b"exact match\n"
                    mock_mmap.return_value = mock_mm

                    result = server._mmap_search("exact match")
                    # Check it returns a string and contains expected content
                    assert isinstance(result, str)
                    assert result == "STRING EXISTS"

            # Test search_string method - FIXED: Mock _mmap_search to return correct values
            with patch.object(server, "_mmap_search", return_value="STRING EXISTS"):
                result = server.search_string("test query")
                assert result == "STRING EXISTS"

            with patch.object(server, "_mmap_search", return_value="STRING NOT FOUND"):
                result = server.search_string("nonexistent")
                assert result == "STRING NOT FOUND"

        finally:
            os.unlink(config_file)

    def test_error_handling_scenarios_fixed(self):
        """Test server error handling with proper return value checking."""
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
                # Check it returns a string
                assert isinstance(result, str)
                # It should indicate the string was not found
                assert result == "STRING NOT FOUND"

            # Test OSError during file operations
            with patch("pathlib.Path.is_file", return_value=True):
                with patch("mmap.mmap", side_effect=OSError("Permission denied")):
                    result = server._mmap_search("test")
                    # Should handle the error gracefully and return a string
                    assert isinstance(result, str)
                    assert result == "STRING NOT FOUND"

            # Test empty file content - create a real empty file and point to it
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as empty_file:
                empty_file_path = empty_file.name

            try:
                # Point the server to the empty file
                server.file_path = Path(empty_file_path)

                result = server._mmap_search("test")
                assert isinstance(result, str)
                assert result == "STRING NOT FOUND"
            finally:
                os.unlink(empty_file_path)

        finally:
            os.unlink(config_file)
