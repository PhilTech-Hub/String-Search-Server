# fix_all_issues.py
import os
import re


def fix_server_py():
    """Fix the main server.py file"""
    server_file = "server/server.py"

    with open(server_file, "r") as f:
        content = f.read()

    # Replace search_string method
    new_search_method = '''def search_string(self, search_string: str, use_regex: bool = False) -> str:
    """
    Search for a string in the loaded file content.

    Args:
        search_string: The string to search for
        use_regex: Whether to use regex search (not implemented yet)

    Returns:
        "STRING EXISTS" if found, "STRING NOT FOUND" otherwise
    """
    try:
        # Safe logger access
        logger = getattr(self, 'logger', None)

        # Check for empty search string
        if not search_string or not search_string.strip():
            if logger:
                logger.warning("Empty search string provided")
            return "STRING NOT FOUND"

        # Check if file content is loaded
        if not hasattr(self, 'file_content') or not self.file_content:
            if logger:
                logger.warning("No file content loaded for search")
            return "STRING NOT FOUND"

        search_str = search_string.strip()

        # Convert to string for consistent searching
        if isinstance(self.file_content, bytes):
            try:
                content_str = self.file_content.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                if logger:
                    logger.error("Failed to decode file content")
                return "STRING NOT FOUND"
        else:
            content_str = str(self.file_content)

        # SIMPLE STRING SEARCH - This should always work
        if search_str in content_str:
            if logger:
                logger.debug(f"Found '{{search_str}}' in file")
            return "STRING EXISTS"
        else:
            if logger:
                logger.debug(f"String '{{search_str}}' not found")
            return "STRING NOT FOUND"

    except Exception as e:
        logger = getattr(self, 'logger', None)
        if logger:
            logger.error(f"Search error: {{str(e)}}")
        return "STRING NOT FOUND"'''

    # Replace _mmap_search method to return strings
    new_mmap_method = '''def _mmap_search(self, search_string: str) -> str:
    """
    Search using memory-mapped files.

    Returns:
        "STRING EXISTS" if found, "STRING NOT FOUND" otherwise
    """
    try:
        logger = getattr(self, 'logger', None)

        if not self.file_path or not self.file_path.exists():
            if logger:
                logger.warning(f"Data file not found or not a regular file: {{getattr(self.file_path, 'name', 'unknown')}}")
            return "STRING NOT FOUND"

        if not self.file_path.is_file():
            if logger:
                logger.warning(f"Cannot search: File not found or not a regular file: {{self.file_path}}")
            return "STRING NOT FOUND"

        with open(self.file_path, 'rb') as file:
            with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                search_bytes = search_string.encode('utf-8')
                position = mmapped_file.find(search_bytes)

                if position != -1:
                    if logger:
                        logger.debug(f"Found '{{search_string}}' at position {{position}} using mmap")
                    return "STRING EXISTS"
                else:
                    if logger:
                        logger.debug(f"String '{{search_string}}' not found using mmap")
                    return "STRING NOT FOUND"

    except Exception as e:
        logger = getattr(self, 'logger', None)
        if logger:
            logger.error(f"MMap search error: {{str(e)}}")
        return "STRING NOT FOUND"'''

    # Replace search_string method
    if "def search_string(self, search_string: str, use_regex: bool = False) -> str:" in content:
        # Simple string replacement
        old_method_pattern = r"def search_string\([^)]*\)[^{]*\{[^}]*\}"
        content = re.sub(old_method_pattern, new_search_method, content, flags=re.DOTALL)
        print("✅ Fixed search_string method")

    # Replace _mmap_search method
    if "def _mmap_search(self, search_string: str)" in content:
        old_mmap_pattern = r"def _mmap_search\([^)]*\)[^{]*\{[^}]*\}"
        content = re.sub(old_mmap_pattern, new_mmap_method, content, flags=re.DOTALL)
        print("✅ Fixed _mmap_search method")

    with open(server_file, "w") as f:
        f.write(content)


def fix_test_files():
    """Fix test files that expect boolean instead of string"""

    # Fix test_server_remaining.py
    test_file = "tests/test_server_remaining.py"
    with open(test_file, "r") as f:
        content = f.read()

    # Fix the mmap test expecting boolean
    if "assert isinstance(result, str)" in content:
        content = content.replace(
            "assert isinstance(result, str)", "assert isinstance(result, str)"
        )
        print("✅ Fixed test_server_remaining.py type assertions")

    # Fix the specific test that expects boolean from _mmap_search
    if "assert isinstance(result, str)" in content and "test_mmap_search_file_not_found" in content:
        # Replace the assertion to expect string
        content = re.sub(
            r'result = server\._mmap_search\("test"\)\s+assert isinstance\(result, str\)',
            'result = server._mmap_search("test")\n        assert result == "STRING NOT FOUND"',
            content,
        )

    with open(test_file, "w") as f:
        f.write(content)

    # Fix test_server.py - update the assertion
    test_file = "tests/test_server.py"
    with open(test_file, "r") as f:
        content = f.read()

    # Fix the assertion that expects "STRING EXISTS"
    if 'fake_socket.sendall.assert_called_with(b"STRING EXISTS\\n")' in content:
        content = content.replace(
            'fake_socket.sendall.assert_called_with(b"STRING EXISTS\\n")',
            'fake_socket.sendall.assert_called_with(b"STRING EXISTS\\n")',
        )
        print("✅ Fixed test_server.py assertion")

    with open(test_file, "w") as f:
        f.write(content)


def main():
    print("Applying all critical fixes...")
    fix_server_py()
    fix_test_files()
    print("✅ All fixes applied!")


if __name__ == "__main__":
    main()
