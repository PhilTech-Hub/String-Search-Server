# test_fixes_fixed.py
from server.server import StringSearchServer
import sys
import os
import tempfile
import logging

sys.path.append(".")


def test_search_fix():
    """Test that the search fix works"""
    print("Testing search functionality...")

    # Create a temporary config file for testing
    config_content = """
host=127.0.0.1
port=44445
file_path=../data/sample_text.txt
reread_on_query=false
ssl_enabled=false
"""

    # Write temporary config file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
        f.write(config_content)
        temp_config_file = f.name

    try:
        # Create server with config file
        server = StringSearchServer(temp_config_file)

        # Ensure logger exists
        if not hasattr(server, "logger"):
            server.logger = logging.getLogger("test_server")
            if not server.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                handler.setFormatter(formatter)
                server.logger.addHandler(handler)
                server.logger.setLevel(logging.INFO)

        # Manually set file content for testing
        test_content = "This is a test file with example content for searching."
        server.file_content = test_content

        print(f"File content set to: '{test_content}'")

        # Test cases that should return "STRING EXISTS"
        should_exist = ["test", "example", "content"]
        for search_str in should_exist:
            result = server.search_string(search_str)
            print(f"Search '{search_str}': {result}")
            if result != "STRING EXISTS":
                print(f"❌ Expected 'STRING EXISTS' for '{search_str}', got '{result}'")
                return False

        # Test cases that should return "STRING NOT FOUND"
        should_not_exist = ["nonexistent", "xyz123", ""]
        for search_str in should_not_exist:
            result = server.search_string(search_str)
            print(f"Search '{search_str}': {result}")
            if result != "STRING NOT FOUND":
                print(f"❌ Expected 'STRING NOT FOUND' for '{search_str}', got '{result}'")
                return False

        # Test type
        result = server.search_string("test")
        if not isinstance(result, str):
            print(f"❌ Expected str, got {type(result)}")
            return False

        print("✅ All search tests passed!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Clean up temp file
        if os.path.exists(temp_config_file):
            os.unlink(temp_config_file)


if __name__ == "__main__":
    test_search_fix()
