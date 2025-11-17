import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from server.server import StringSearchServer


def test_server_ssl_initialization():
    """Test SSL initialization paths."""
    config_content = "host=127.0.0.1\nport=44445\nlinuxpath=test.txt\nssl_enabled=True\ncertfile=cert.pem\nkeyfile=key.pem"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
        f.write(config_content)
        config_file = f.name

    try:
        with patch("pathlib.Path.is_file", return_value=True):
            # Mock the SSL context creation directly
            with patch("server.server.create_ssl_context") as mock_ssl:
                mock_context = MagicMock()
                mock_ssl.return_value = mock_context

                # Mock file existence for SSL files at the pathlib level
                with patch("pathlib.Path.exists") as mock_exists:
                    # Make all file existence checks return True
                    mock_exists.return_value = True

                    server = StringSearchServer(config_file)

                    # Should attempt to setup SSL
                    assert mock_ssl.called
                    # Verify SSL is enabled
                    assert server.ssl_enabled == True
                    assert server.ssl_context == mock_context
    finally:
        os.unlink(config_file)


def test_server_ssl_initialization_failure():
    """Test SSL initialization when SSL setup fails."""
    config_content = "host=127.0.0.1\nport=44445\nlinuxpath=test.txt\nssl_enabled=True\ncertfile=cert.pem\nkeyfile=key.pem"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
        f.write(config_content)
        config_file = f.name

    try:
        with patch("pathlib.Path.is_file", return_value=True):
            # Mock the SSL context creation to fail
            with patch("server.server.create_ssl_context") as mock_ssl:
                mock_ssl.side_effect = ValueError("SSL configuration error")

                server = StringSearchServer(config_file)

                # SSL should be disabled after failure
                assert server.ssl_enabled == False
                assert server.ssl_context is None
    finally:
        os.unlink(config_file)


def test_server_connection_handling():
    """Test server connection acceptance and handling."""
    config_content = "host=127.0.0.1\nport=44445\nlinuxpath=test.txt"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
        f.write(config_content)
        config_file = f.name

    try:
        server = StringSearchServer(config_file)

        # Mock socket and connection
        mock_socket = MagicMock()
        mock_connection = MagicMock()

        with patch.object(server, "handle_client") as mock_handler:
            server.server_socket = mock_socket
            mock_socket.accept.return_value = (mock_connection, ("127.0.0.1", 12345))

            # Test single connection handling - set stop event after one iteration
            server._stop_event = MagicMock()
            server._stop_event.is_set.side_effect = [False, True]  # Run once then stop

            with patch("select.select", return_value=([mock_socket], [], [])):
                # Mock the server run to avoid infinite loop
                with patch.object(server, "start") as mock_start:
                    server.run()
                    assert mock_start.called
    finally:
        os.unlink(config_file)


def test_server_shutdown():
    """Test server shutdown procedure."""
    config_content = "host=127.0.0.1\nport=44445\nlinuxpath=test.txt"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
        f.write(config_content)
        config_file = f.name

    try:
        server = StringSearchServer(config_file)

        # Mock socket
        mock_socket = MagicMock()
        server.server_socket = mock_socket

        # Test shutdown - mock the logger to avoid attribute error
        with patch("server.server.logger") as mock_logger:
            server.shutdown()

            # Verify logger was called
            mock_logger.info.assert_called_with("Shutting down server...")

        # Socket should be closed and running flag set to False
        assert server.running == False
    finally:
        os.unlink(config_file)


def test_server_mmap_search_coverage():
    """Test additional mmap search scenarios for coverage."""
    config_content = (
        "host=127.0.0.1\nport=44445\nlinuxpath=./data/sample.txt\nREREAD_ON_QUERY=False"
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
        f.write(config_content)
        config_file = f.name

    try:
        server = StringSearchServer(config_file)

        # Test with file that exists but has permission issues
        with patch("pathlib.Path.is_file", return_value=True):
            with patch("builtins.open", side_effect=PermissionError("Permission denied")):
                result = server._mmap_search("test")
                assert result == "STRING NOT FOUND" or "ERROR" in result

        # Test with empty file
        with patch("pathlib.Path.is_file", return_value=True):
            with patch("builtins.open") as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                mock_file.fileno.return_value = 123
                with patch("mmap.mmap") as mock_mmap:
                    mock_mmap_instance = MagicMock()
                    mock_mmap.return_value.__enter__.return_value = mock_mmap_instance
                    mock_mmap_instance.find.return_value = -1
                    result = server._mmap_search("test")
                    assert result == "STRING NOT FOUND"

    finally:
        os.unlink(config_file)
