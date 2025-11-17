#!/usr/bin/env python3
"""
Common PEP 8 Issue Fixer
Targeted fixes for specific PEP 8 violations.
"""

import re
import os
from pathlib import Path


class PEP8IssueFixer:
    """Fix common PEP 8 issues that automated tools might miss."""

    def __init__(self):
        self.fixes_applied = 0

    def fix_trailing_whitespace(self, content):
        """Remove trailing whitespace from lines."""
        original_lines = content.split("\n")
        fixed_lines = [line.rstrip() for line in original_lines]
        if original_lines != fixed_lines:
            self.fixes_applied += 1
        return "\n".join(fixed_lines)

    def fix_mixed_tabs_spaces(self, content):
        """Replace tabs with 4 spaces."""
        if "\t" in content:
            self.fixes_applied += 1
            return content.replace("\t", "    ")
        return content

    def fix_multiple_blank_lines(self, content):
        """Replace multiple consecutive blank lines with maximum of 2."""
        # Replace 3 or more blank lines with 2 blank lines
        fixed = re.sub(r"\n\s*\n\s*\n+", "\n\n\n", content)
        # Then replace remaining sequences of 3+ with 2
        fixed = re.sub(r"(\n\s*){3,}", "\n\n", fixed)
        if fixed != content:
            self.fixes_applied += 1
        return fixed

    def fix_import_spacing(self, content):
        """Ensure proper spacing around imports."""
        lines = content.split("\n")
        fixed_lines = []
        in_import_block = False
        previous_was_import = False

        for line in lines:
            stripped = line.strip()
            is_import = stripped.startswith(("import ", "from "))

            if is_import:
                if not in_import_block and previous_was_import and fixed_lines:
                    # Add blank line before new import block
                    if fixed_lines[-1].strip() != "":
                        fixed_lines.append("")
                in_import_block = True
                previous_was_import = True
            else:
                if in_import_block and not is_import and stripped != "":
                    # Add blank line after import block
                    if fixed_lines[-1].strip() != "":
                        fixed_lines.append("")
                    in_import_block = False
                previous_was_import = False

            fixed_lines.append(line)

        fixed_content = "\n".join(fixed_lines)
        if fixed_content != content:
            self.fixes_applied += 1
        return fixed_content

    def fix_function_spacing(self, content):
        """Ensure proper spacing around functions (2 blank lines)."""
        # This is complex, so we'll use a simpler approach
        # Remove excessive blank lines between functions
        fixed = re.sub(r"(\n\s*){4,}", "\n\n\n", content)
        if fixed != content:
            self.fixes_applied += 1
        return fixed

    def fix_comment_spacing(self, content):
        """Ensure comments have proper spacing."""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Fix: At least two spaces before inline comment
            if "            #" in line and not line.strip().startswith("#"):
                code_part = line.split("            #")[0].rstrip()
                comment_part = "            #" + "#".join(line.split("#")[1:])
                if not code_part.endswith("  ") and not code_part.endswith("\t"):
                    line = code_part + "  " + comment_part
                    self.fixes_applied += 1
            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_file(self, file_path):
        """Apply all fixes to a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply fixes in sequence
            content = self.fix_trailing_whitespace(content)
            content = self.fix_mixed_tabs_spaces(content)
            content = self.fix_multiple_blank_lines(content)
            content = self.fix_import_spacing(content)
            content = self.fix_function_spacing(content)
            content = self.fix_comment_spacing(content)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            return False

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False

    def fix_project(self, project_dir="."):
        """Fix all Python files in the project."""
        python_files = []

        for root, dirs, files in os.walk(project_dir):
            # Skip common directories
            dirs[:] = [
                d
                for d in dirs
                if d
                not in {
                    "__pycache__",
                    ".pytest_cache",
                    ".mypy_cache",
                    "venv",
                    "env",
                    ".venv",
                    "node_modules",
                }
            ]

            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

        print(f"🔧 Fixing {len(python_files)} Python files...")

        fixed_count = 0
        for file_path in python_files:
            if self.fix_file(file_path):
                fixed_count += 1
                print(f"✅ Fixed: {file_path}")

        print(f"\n🎯 Fixed {fixed_count} files with {self.fixes_applied} individual fixes")
        return fixed_count


def main():
    fixer = PEP8IssueFixer()
    fixer.fix_project()

    if fixer.fixes_applied > 0:
        print("\n💡 Run the PEP 8 compliance checker to verify fixes:")
        print("  python scripts/verify_pep8_compliance.py")
    else:
        print("\n✅ No common PEP 8 issues found!")


if __name__ == "__main__":
    main()
