#!/usr/bin/env python3
"""
Completely restore the corrupted config test file
"""
from pathlib import Path


def restore_config_test_file():
    """Completely rewrite the config test file"""
    content = '''"""
Fixed config parsing coverage tests with correct key names.
"""

import pytest
import tempfile
import os
from pathlib import Path
from server.config import Config

class TestConfigCoverageFixed:
    """Fixed config parsing tests with correct key names."""

    def test_config_parsing_coverage_fixed(self):
        """Cover all config parsing scenarios with correct key names."""
        test_cases = [
            # Basic valid config - using correct key names from your actual code
            {"content": "host=127.0.0.1\\nport=44445\\nlinuxpath=test.txt", "should_work": True},
            # Missing required fields
            {"content": "host=127.0.0.1", "should_work": False},
            # Invalid port
            {"content": "host=127.0.0.1\\nport=999999\\nlinuxpath=test.txt", "should_work": False},
            # SSL configuration
            {"content": "host=127.0.0.1\\nport=44445\\nlinuxpath=test.txt\\nssl_enabled=true", "should_work": True},
        ]

        for i, test_case in enumerate(test_cases):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
                f.write(test_case["content"])
                config_file = f.name

            try:
                if test_case["should_work"]:
                    config = Config(config_file)
                    assert config is not None
                else:
                    with pytest.raises((ValueError, FileNotFoundError)):
                        Config(config_file)
            finally:
                Path(config_file).unlink(missing_ok=True)

    def test_config_edge_cases(self):
        """Test configuration edge cases."""
        test_cases = [
            # Missing required fields
            {"content": "host=127.0.0.1", "should_work": False},
            # Invalid port
            {"content": "host=127.0.0.1\\nport=999999\\nlinuxpath=test.txt", "should_work": False},
            # Valid config with SSL
            {"content": "host=127.0.0.1\\nport=44445\\nlinuxpath=test.txt\\nssl_enabled=true", "should_work": True},
        ]

        for i, test_case in enumerate(test_cases):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
                f.write(test_case["content"])
                config_file = f.name

            try:
                if test_case["should_work"]:
                    config = Config(config_file)
                    assert config is not None
                else:
                    with pytest.raises((ValueError, FileNotFoundError)):
                        Config(config_file)
            finally:
                Path(config_file).unlink(missing_ok=True)
'''

    Path("tests/test_config_coverage_fixed.py").write_text(content)
    print("✅ Config test file completely restored!")


if __name__ == "__main__":
    restore_config_test_file()
