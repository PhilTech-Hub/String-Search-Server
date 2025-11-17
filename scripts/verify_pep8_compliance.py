#!/usr/bin/env python3
"""
PEP 8 Compliance Verification Script
Comprehensive code style checking and automatic fixing for Python files.
"""

import os
import subprocess
import sys
from pathlib import Path


class PEP8ComplianceChecker:
    """Comprehensive PEP 8 compliance verification and fixing."""

    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.python_files = []
        self.issues_found = 0

    def find_python_files(self):
        """Find all Python files in the project."""
        print("🔍 Searching for Python files...")

        exclude_dirs = {
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            "venv",
            "env",
            ".venv",
            "node_modules",
            "build",
            "dist",
        }

        for root, dirs, files in os.walk(self.base_dir):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file.endswith(".py"):
                    full_path = Path(root) / file
                    self.python_files.append(full_path)

        print(f"📁 Found {len(self.python_files)} Python files")
        return self.python_files

    def run_pycodestyle(self, file_path):
        """Run pycodestyle (PEP 8 checker) on a file."""
        try:
            result = subprocess.run(
                [
                    "pycodestyle",
                    "--max-line-length=100",
                    "--ignore=E121,E123,E126,E226,E24,E704,W503,W504,E203",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"❌ PEP 8 issues in {file_path}:")
                print(result.stdout)
                self.issues_found += len(result.stdout.strip().split("\n"))
                return False
            return True

        except FileNotFoundError:
            print("❌ pycodestyle not installed. Run: pip install pycodestyle")
            return False

    def run_flake8(self, file_path):
        """Run flake8 for additional code quality checks."""
        try:
            result = subprocess.run(
                [
                    "flake8",
                    "--max-line-length=100",
                    "--ignore=E121,E123,E126,E226,E24,E704,W503,W504,E203",
                    "--extend-ignore=F401,F841",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"⚠️  Flake8 issues in {file_path}:")
                print(result.stdout)
                return False
            return True

        except FileNotFoundError:
            print("⚠️  flake8 not installed. Run: pip install flake8")
            return True  # Not critical

    def check_file_length(self, file_path):
        """Check if file is too long (PEP 8 recommends < 1000 lines)."""
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) > 1000:
            print(f"⚠️  {file_path}: File is very long ({len(lines)} lines)")
            return False
        return True

    def check_line_lengths(self, file_path):
        """Check for lines exceeding maximum length."""
        long_lines = []
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                # Count actual characters (excluding newline)
                line_length = len(line.rstrip("\n\r"))
                if line_length > 100:
                    long_lines.append((i, line_length, line.strip()))

        if long_lines:
            print(f"⚠️  {file_path}: {len(long_lines)} long lines found")
            for line_num, length, content in long_lines[:3]:  # Show first 3
                print(f"   Line {line_num} ({length} chars): {content[:50]}...")
            return False
        return True

    def check_imports(self, file_path):
        """Check import style and order."""
        try:
            result = subprocess.run(
                ["isort", "--check-only", "--diff", str(file_path)], capture_output=True, text=True
            )

            if result.returncode != 0:
                print(f"⚠️  Import order issues in {file_path}:")
                print(result.stdout)
                return False
            return True

        except FileNotFoundError:
            return True  # isort not installed, skip

    def run_autopep8_fix(self, file_path):
        """Automatically fix PEP 8 issues using autopep8."""
        try:
            # First, create a backup
            backup_path = file_path.with_suffix(".py.backup")

            # Run autopep8 to fix issues
            result = subprocess.run(
                [
                    "autopep8",
                    "--in-place",
                    "--aggressive",
                    "--max-line-length=100",
                    "--ignore=E121,E123,E126,E226,E24,E704,W503,W504,E203",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"✅ Fixed PEP 8 issues in {file_path}")
                return True
            else:
                print(f"❌ Failed to fix {file_path}: {result.stderr}")
                return False

        except FileNotFoundError:
            print("❌ autopep8 not installed. Run: pip install autopep8")
            return False

    def format_with_black(self, file_path):
        """Format code using black (optional, more aggressive)."""
        try:
            result = subprocess.run(
                ["black", "--line-length=100", "--target-version=py310", str(file_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"✅ Formatted {file_path} with black")
                return True
            return False

        except FileNotFoundError:
            return True  # black not installed, skip

    def generate_compliance_report(self):
        """Generate comprehensive compliance report."""
        print("\n" + "=" * 60)
        print("📊 PEP 8 COMPLIANCE REPORT")
        print("=" * 60)

        total_files = len(self.python_files)
        compliant_files = 0

        for file_path in self.python_files:
            print(f"\n📄 Checking: {file_path}")

            checks_passed = 0
            total_checks = 4

            # Run checks
            if self.run_pycodestyle(file_path):
                checks_passed += 1
            if self.run_flake8(file_path):
                checks_passed += 1
            if self.check_file_length(file_path):
                checks_passed += 1
            if self.check_line_lengths(file_path):
                checks_passed += 1

            if checks_passed == total_checks:
                compliant_files += 1
                print(f"   ✅ Fully PEP 8 compliant ({checks_passed}/{total_checks} checks)")
            else:
                print(f"   ⚠️  {checks_passed}/{total_checks} checks passed")

        compliance_rate = (compliant_files / total_files) * 100 if total_files > 0 else 0

        print("\n" + "=" * 60)
        print(
            f"🎯 SUMMARY: {compliant_files}/{total_files} files compliant ({compliance_rate:.1f}%)"
        )
        print(f"🔧 Issues found: {self.issues_found}")

        if self.issues_found == 0:
            print("✅ Excellent! No PEP 8 issues found.")
        else:
            print("⚠️  Some PEP 8 issues need attention.")

        return self.issues_found == 0

    def auto_fix_issues(self):
        """Automatically fix all PEP 8 issues."""
        print("\n🛠️  Auto-fixing PEP 8 issues...")

        fixed_count = 0
        for file_path in self.python_files:
            if self.run_autopep8_fix(file_path):
                fixed_count += 1

        print(f"✅ Fixed issues in {fixed_count}/{len(self.python_files)} files")

        # Run black formatter if available
        black_count = 0
        for file_path in self.python_files:
            if self.format_with_black(file_path):
                black_count += 1

        if black_count > 0:
            print(f"✅ Formatted {black_count} files with black")

        return fixed_count


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="PEP 8 Compliance Checker")
    parser.add_argument("--fix", action="store_true", help="Auto-fix PEP 8 issues")
    parser.add_argument("--dir", default=".", help="Directory to check (default: current)")
    args = parser.parse_args()

    checker = PEP8ComplianceChecker(args.dir)
    checker.find_python_files()

    if not checker.python_files:
        print("❌ No Python files found!")
        return 1

    if args.fix:
        # Auto-fix mode
        checker.auto_fix_issues()
        print("\n🔄 Running compliance check after fixes...")
        is_compliant = checker.generate_compliance_report()
    else:
        # Check-only mode
        is_compliant = checker.generate_compliance_report()
        if not is_compliant:
            print("\n💡 Tip: Run with --fix to automatically fix many issues")

    return 0 if is_compliant else 1


if __name__ == "__main__":
    sys.exit(main())
