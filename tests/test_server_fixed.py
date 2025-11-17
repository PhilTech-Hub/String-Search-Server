import unittest
import logging
import threading
from io import StringIO
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from server.server import StringSearchServer


class TestStringSearchServerFull(unittest.TestCase):
    """Comprehensive tests for StringSearchServer."""

    def setUp(self):
        self.config_file = "tests/test_config.conf"  # Use SSL-disabled config
        self.fake_lines = ["line1", "line2", "line3"]

    @patch("pathlib.Path.open", new_callable=mock_open, read_data="line1\nline2\nline3\n")
    @patch("pathlib.Path.is_file", return_value=True)
    def test_load_file_once(self, mock_is_file, mock_open_file):
        server = StringSearchServer(config_file=self.config_file)
        server.reread_on_query = False
        self.assertEqual(len(server.file_lines), 3)
        self.assertIn("line1", server.file_lines)

    @patch("pathlib.Path.open", new_callable=mock_open)
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("mmap.mmap")
    def test_mmap_search_first_last_empty(self, mock_mmap, mock_is_file, mock_file):
        # Simulate mmap.find behavior
        mock_mm = MagicMock()
        mock_mm.find.side_effect = lambda pattern: 0 if b"line1" in pattern else -1

        def smart_rfind(pattern):
            if b"line3" in pattern:
                return len(b"line1\nline2\nline3") - len(b"line3")
            return -1

        mock_mm.rfind.side_effect = smart_rfind
        mock_mmap.return_value = mock_mm

        server = StringSearchServer(config_file=self.config_file)
        # Test mmap search functionality
        result = server._mmap_search("line1")
        self.assertEqual(result, "STRING EXISTS")

    @patch("pathlib.Path.open", new_callable=mock_open)
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("mmap.mmap", side_effect=OSError)
    def test_mmap_search_oserror(self, mock_mmap, mock_is_file, mock_file):
        server = StringSearchServer(config_file=self.config_file)
        # Should handle OSError gracefully
        result = server._mmap_search("test")
        self.assertEqual(result, "STRING NOT FOUND")

    @patch("pathlib.Path.open", new_callable=mock_open)
    @patch("pathlib.Path.is_file", return_value=True)
    def test_handle_client_empty_query(self, mock_is_file, mock_file):
        fake_socket = MagicMock()
        fake_socket.recv.side_effect = [b"\n", b""]
        server = StringSearchServer(config_file=self.config_file)
        server.handle_client(fake_socket, ("127.0.0.1", 12345))
        # Should handle empty query without crashing

    @patch("pathlib.Path.open", new_callable=mock_open)
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("mmap.mmap")
    def test_reread_on_query_enabled(self, mock_mmap, mock_is_file, mock_file):
        mock_mm = MagicMock()
        mock_mm.find.side_effect = lambda pattern: 0 if b"line3" in pattern else -1
        mock_mm.rfind.return_value = len(b"line1\nline2\nline3") - len(b"line3")
        mock_mmap.return_value = mock_mm

        fake_socket = MagicMock()
        fake_socket.recv.side_effect = [b"line3\n", b""]
        server = StringSearchServer(config_file=self.config_file)
        server.reread_on_query = True
        server.handle_client(fake_socket, ("127.0.0.1", 12345))
        # Should handle query with reread enabled


if __name__ == "__main__":
    unittest.main()
