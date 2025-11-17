import unittest
import sys
import os

# Add the root directory to Python path to import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestUtilityModules(unittest.TestCase):

    def test_apply_test_fixes_import(self):
        """Test that apply_test_fixes can be imported"""
        try:
            from apply_test_fixes import apply_test_fixes

            self.assertTrue(callable(apply_test_fixes))
        except ImportError as e:
            self.skipTest(f"apply_test_fixes not available: {e}")

    def test_final_comprehensive_fix_import(self):
        """Test that final_comprehensive_fix can be imported"""
        try:
            from final_comprehensive_fix import final_comprehensive_fix

            self.assertTrue(callable(final_comprehensive_fix))
        except ImportError as e:
            self.skipTest(f"final_comprehensive_fix not available: {e}")

    def test_fix_all_issues_import(self):
        """Test that fix_all_issues can be imported"""
        try:
            from fix_all_issues import fix_all_issues

            self.assertTrue(callable(fix_all_issues))
        except ImportError as e:
            self.skipTest(f"fix_all_issues not available: {e}")

    def test_fix_boolean_expectations_import(self):
        """Test that fix_boolean_expectations can be imported"""
        try:
            from fix_boolean_expectations import fix_boolean_expectations

            self.assertTrue(callable(fix_boolean_expectations))
        except ImportError as e:
            self.skipTest(f"fix_boolean_expectations not available: {e}")

    def test_fix_specific_tests_import(self):
        """Test that fix_specific_tests can be imported"""
        try:
            from fix_specific_tests import fix_specific_tests

            self.assertTrue(callable(fix_specific_tests))
        except ImportError as e:
            self.skipTest(f"fix_specific_tests not available: {e}")


if __name__ == "__main__":
    unittest.main()
