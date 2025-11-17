import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os

from server.ssl_utils import create_ssl_context


class TestSSLUtilsCoverageFixed(unittest.TestCase):

    def test_create_ssl_context_success(self):
        """Test successful SSL context creation"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False) as cert_file:
            cert_file.write("fake cert content")
            cert_path = cert_file.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".key", delete=False) as key_file:
            key_file.write("fake key content")
            key_path = key_file.name

        try:
            # Mock ssl context to avoid actual SSL operations
            with patch("ssl.create_default_context") as mock_ssl:
                mock_context = MagicMock()
                mock_ssl.return_value = mock_context

                context = create_ssl_context(cert_path, key_path)
                self.assertEqual(context, mock_context)

        finally:
            os.unlink(cert_path)
            os.unlink(key_path)

    def test_create_ssl_context_no_cert_files(self):
        """Test SSL context creation without certificate files"""
        # This should raise ValueError as expected by the function
        with self.assertRaises(ValueError):
            create_ssl_context(None, None)

    def test_create_ssl_context_missing_files(self):
        """Test SSL context creation with missing files"""
        # This should raise FileNotFoundError as expected by the function
        with self.assertRaises(FileNotFoundError):
            create_ssl_context("nonexistent.crt", "nonexistent.key")

    def test_create_ssl_context_ssl_errors(self):
        """Test SSL context creation with SSL errors"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False) as cert_file:
            cert_file.write("fake cert content")
            cert_path = cert_file.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".key", delete=False) as key_file:
            key_file.write("fake key content")
            key_path = key_file.name

        try:
            # Test SSL error during context creation
            with patch("ssl.create_default_context", side_effect=Exception("SSL error")):
                # This should raise RuntimeError as per the function's exception handling
                with self.assertRaises(RuntimeError):
                    create_ssl_context(cert_path, key_path)

        finally:
            os.unlink(cert_path)
            os.unlink(key_path)

    def test_create_ssl_context_various_scenarios(self):
        """Test various SSL context creation scenarios"""
        # Test with only cert file - should raise ValueError
        with self.assertRaises(ValueError):
            create_ssl_context("dummy.crt", None)

        # Test with only key file - should raise ValueError
        with self.assertRaises(ValueError):
            create_ssl_context(None, "dummy.key")


if __name__ == "__main__":
    unittest.main()
