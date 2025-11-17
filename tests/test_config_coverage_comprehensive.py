import unittest
from unittest.mock import patch, mock_open
import tempfile
import os

from server.config import Config


class TestConfigCoverageComprehensive(unittest.TestCase):

    def test_config_initialization_edge_cases(self):
        """Test Config initialization with various edge cases"""
        # Test with non-existent config file
        with self.assertRaises(FileNotFoundError):
            Config("nonexistent.conf")

    def test_config_parsing_comprehensive(self):
        """Test comprehensive config parsing scenarios"""
        # Test minimal valid config with linuxpath
        config_content = """
linuxpath = tests/test_data/sample_text.txt
host = localhost
port = 8888
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            config = Config(config_file)
            self.assertEqual(config.host, "localhost")
            self.assertEqual(config.port, 8888)
            self.assertEqual(config.linuxpath, "tests/test_data/sample_text.txt")
            self.assertFalse(config.reread_on_query)  # Default value
            self.assertFalse(config.ssl_enabled)  # Default value
        finally:
            os.unlink(config_file)

    def test_config_with_all_options(self):
        """Test config with all possible options"""
        config_content = """
linuxpath = tests/test_data/sample_text.txt
host = 127.0.0.1
port = 9999
reread_on_query = true
ssl_enabled = true
certfile = cert.pem
keyfile = key.pem
cafile = ca.pem
psk = mypresharedkey
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            config = Config(config_file)
            self.assertEqual(config.host, "127.0.0.1")
            self.assertEqual(config.port, 9999)
            self.assertEqual(config.linuxpath, "tests/test_data/sample_text.txt")
            self.assertTrue(config.reread_on_query)
            self.assertTrue(config.ssl_enabled)
            self.assertEqual(config.certfile, "cert.pem")
            self.assertEqual(config.keyfile, "key.pem")
            self.assertEqual(config.cafile, "ca.pem")
            self.assertEqual(config.psk, "mypresharedkey")
        finally:
            os.unlink(config_file)

    def test_config_missing_required_fields(self):
        """Test config with missing required fields"""
        config_content = """
host = localhost
port = 8888
# Missing linuxpath - should fail
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            with self.assertRaises(ValueError):
                Config(config_file)
        finally:
            os.unlink(config_file)

    def test_config_invalid_values(self):
        """Test config with invalid values"""
        config_content = """
linuxpath = tests/test_data/sample_text.txt
host = localhost
port = not_a_number
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            with self.assertRaises(ValueError):
                Config(config_file)
        finally:
            os.unlink(config_file)


if __name__ == "__main__":
    unittest.main()
