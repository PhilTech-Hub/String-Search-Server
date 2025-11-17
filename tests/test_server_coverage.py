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
