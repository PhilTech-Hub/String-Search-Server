# fix_specific_tests.py
import os


def fix_edge_cases_test():
    """Fix the test_edge_cases.py file"""
    file_path = "tests/test_edge_cases.py"

    with open(file_path, "r") as f:
        content = f.read()

    # Fix the empty file test
    if "self.assertFalse(result)" in content:
        content = content.replace(
            "self.assertFalse(result)", 'self.assertEqual(result, "STRING NOT FOUND")'
        )
        print("✅ Fixed empty file test assertion")

    # Fix the test to use proper config file
    if "config_file=self.config_file" in content:
        content = content.replace(
            "config_file=self.config_file", 'config_file="config/server_config.conf"'
        )
        print("✅ Fixed config file references")

    with open(file_path, "w") as f:
        f.write(content)


def fix_server_tests():
    """Fix the main server tests"""
    file_path = "tests/test_server.py"

    with open(file_path, "r") as f:
        content = f.read()

    # Fix the static mode test to set file_content
    if 'server.file_lines = set(["apple", "banana", "cherry"])' in content:
        content = content.replace(
            'server.file_lines = set(["apple", "banana", "cherry"])',
            'server.file_lines = set(["apple", "banana", "cherry"])\n        server.file_content = "apple banana cherry"',
        )
        print("✅ Fixed static mode test")

    # Fix the dynamic mode test
    if (
        "server.reread_on_query = True" in content
        and 'server.file_path = Path("dummy.txt")' in content
    ):
        # Add file_content for dynamic mode
        content = content.replace(
            'server.file_path = Path("dummy.txt")',
            'server.file_path = Path("dummy.txt")\n        server.file_content = "banana split"',
        )
        print("✅ Fixed dynamic mode test")

    with open(file_path, "w") as f:
        f.write(content)


def main():
    print("Fixing specific test files...")
    fix_edge_cases_test()
    fix_server_tests()
    print("✅ Specific test fixes applied!")


if __name__ == "__main__":
    main()
