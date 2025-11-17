# verify_fixes.py
import sys
import os

sys.path.append(".")


def test_basic_search():
    """Test that basic search works"""
    from server.server import StringSearchServer

    print("Testing basic search functionality...")

    # Test with sample config
    config_file = "config/server_config.conf"
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        return False

    try:
        server = StringSearchServer(config_file)

        # Test 1: Set file_content directly
        server.file_content = "apple banana cherry"
        result1 = server.search_string("apple")
        print(f"Search 'apple': {result1}")
        assert result1 == "STRING EXISTS", f"Expected 'STRING EXISTS', got '{result1}'"

        # Test 2: String not found
        result2 = server.search_string("orange")
        print(f"Search 'orange': {result2}")
        assert result2 == "STRING NOT FOUND", f"Expected 'STRING NOT FOUND', got '{result2}'"

        # Test 3: Empty search
        result3 = server.search_string("")
        print(f"Search '': {result3}")
        assert result3 == "STRING NOT FOUND", f"Expected 'STRING NOT FOUND', got '{result3}'"

        print("✅ All basic search tests passed!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_mmap_search():
    """Test mmap search functionality"""
    from server.server import StringSearchServer

    print("Testing mmap search functionality...")

    config_file = "config/server_config.conf"
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        return False

    try:
        server = StringSearchServer(config_file)

        # Test with non-existent file
        result = server._mmap_search("test")
        print(f"MMap search (file not found): {result}")
        assert result == "STRING NOT FOUND", f"Expected 'STRING NOT FOUND', got '{result}'"
        assert isinstance(result, str), f"Expected string, got {type(result)}"

        print("✅ MMap search test passed!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success1 = test_basic_search()
    success2 = test_mmap_search()

    if success1 and success2:
        print("🎉 All verification tests passed!")
    else:
        print("💥 Some verification tests failed!")
        sys.exit(1)
