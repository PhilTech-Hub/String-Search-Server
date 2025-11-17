#!/usr/bin/env python3
"""
Error Message Improvement Validation
Verify that error messages are now user-friendly and informative.
"""

import tempfile
import os
from pathlib import Path


def validate_error_messages():
    """Test that error messages are improved."""

    print("🔍 Validating Improved Error Messages...\n")

    improvements_verified = []

    # Test 1: Missing configuration file
    print("1. Testing missing config file:")
    try:
        from server.server import StringSearchServer

        server = StringSearchServer("nonexistent_config.conf")
    except Exception as e:
        error_msg = str(e)
        print(f"   Error: {error_msg}")
        if "configuration" in error_msg.lower() or "config" in error_msg.lower():
            improvements_verified.append("✅ Server config errors are descriptive")
        else:
            improvements_verified.append("❌ Server config errors need improvement")

    # Test 2: Client empty query validation
    print("\n2. Testing empty query validation:")
    from client.client import StringSearchClient
    from unittest.mock import patch, MagicMock

    with patch("socket.socket") as mock_socket:
        fake_socket = MagicMock()
        fake_socket.recv.return_value = b"STRING NOT FOUND\n"
        mock_socket.return_value = fake_socket

        client = StringSearchClient(host="127.0.0.1", port=44445, use_ssl=False)
        client.connect()

        try:
            client.send_query("")
        except ValueError as e:
            print(f"   Error: {e}")
            if "cannot be empty" in str(e).lower():
                improvements_verified.append("✅ Empty query validation is clear")
            else:
                improvements_verified.append("❌ Empty query validation needs improvement")
        client.close()

    # Test 3: SSL certificate errors
    print("\n3. Testing SSL error messages:")
    try:
        from server.ssl_utils import create_ssl_context

        create_ssl_context(certfile="missing.crt", keyfile="missing.key")
    except (ValueError, FileNotFoundError) as e:
        print(f"   Error: {e}")
        if "certificate" in str(e).lower() or "file not found" in str(e).lower():
            improvements_verified.append("✅ SSL error messages are specific")
        else:
            improvements_verified.append("❌ SSL error messages need improvement")

    # Test 4: File permission errors
    print("\n4. Testing file permission errors:")
    try:
        # Create a temporary file and make it inaccessible
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_file = f.name

        # Make file read-only to test permission errors
        os.chmod(temp_file, 0o000)

        from server.server import StringSearchServer

        server = StringSearchServer.__new__(StringSearchServer)
        server.file_path = Path(temp_file)

        result = server._mmap_search("test")
        print(f"   Search result: {result}")

    except Exception as e:
        print(f"   Error: {e}")
        if "permission" in str(e).lower():
            improvements_verified.append("✅ File permission errors are clear")
        else:
            improvements_verified.append("❌ File permission errors need improvement")
    finally:
        # Restore permissions and cleanup
        try:
            os.chmod(temp_file, 0o644)
            os.unlink(temp_file)
        except BaseException:
            pass

    # Print validation results
    print("\n📋 Error Message Improvement Report:")
    for item in improvements_verified:
        print(f"  {item}")

    # Overall assessment
    if all("✅" in item for item in improvements_verified):
        print("\n🎉 SUCCESS: All error messages are now user-friendly and informative!")
        return True
    else:
        print("\n⚠️  Some error messages still need improvement.")
        return False


if __name__ == "__main__":
    validate_error_messages()
