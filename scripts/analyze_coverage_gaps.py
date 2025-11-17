#!/usr/bin/env python3
"""
COVERAGE GAP ANALYZER
Identifies specific lines and functions missing test coverage.
"""

import json
from pathlib import Path
import subprocess


class CoverageGapAnalyzer:
    def __init__(self):
        self.coverage_data = {}
        self.gaps = []

    def load_coverage_data(self):
        """Load coverage data from JSON file."""
        # Generate coverage JSON
        subprocess.run(
            ["python", "-m", "coverage", "json", "-o", "coverage_details.json"], capture_output=True
        )

        if Path("coverage_details.json").exists():
            with open("coverage_details.json", "r") as f:
                self.coverage_data = json.load(f)
            return True
        return False

    def analyze_gaps(self):
        """Analyze coverage gaps and generate recommendations."""
        if not self.coverage_data:
            print("❌ No coverage data found. Run tests first.")
            return

        print("🔍 ANALYZING COVERAGE GAPS...")
        print("=" * 60)

        for file_path, file_data in self.coverage_data["files"].items():
            if "test" not in file_path and file_path.endswith(".py"):
                self._analyze_file_gaps(file_path, file_data)

        self._generate_gap_report()

    def _analyze_file_gaps(self, file_path, file_data):
        """Analyze gaps for a specific file."""
        missing_lines = file_data.get("missing_lines", [])
        if missing_lines:
            coverage_pct = file_data.get("summary", {}).get("percent_covered", 0)

            if coverage_pct < 90:  # Focus on files with poor coverage
                gap_info = {
                    "file": file_path,
                    "coverage_percent": coverage_pct,
                    "missing_lines": missing_lines,
                    "total_lines": file_data.get("summary", {}).get("num_statements", 0),
                    "missing_functions": self._identify_missing_functions(file_path, missing_lines),
                }
                self.gaps.append(gap_info)

    def _identify_missing_functions(self, file_path, missing_lines):
        """Identify which functions have missing coverage."""
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()

            missing_functions = []
            current_function = None
            function_start = 0

            for i, line in enumerate(lines, 1):
                # Track function definitions
                if line.strip().startswith("def "):
                    if current_function and any(
                        missing for missing in missing_lines if function_start <= missing <= i - 1
                    ):
                        missing_functions.append(current_function)

                    current_function = line.strip().split("def ")[1].split("(")[0]
                    function_start = i

                # Track class definitions
                elif line.strip().startswith("class "):
                    current_function = f"Class: {
                        line.strip().split('class ')[1].split('(')[0].split(':')[0]}"
                    function_start = i

            # Check last function
            if current_function and any(
                missing for missing in missing_lines if function_start <= missing <= len(lines)
            ):
                missing_functions.append(current_function)

            return missing_functions

        except Exception as e:
            return [f"Error analyzing functions: {e}"]

    def _generate_gap_report(self):
        """Generate detailed gap report."""
        if not self.gaps:
            print("🎉 No significant coverage gaps found!")
            return

        print(f"\n🚨 FOUND {len(self.gaps)} FILES WITH COVERAGE GAPS:")
        print("=" * 60)

        # Sort by worst coverage first
        self.gaps.sort(key=lambda x: x["coverage_percent"])

        for gap in self.gaps[:10]:  # Show top 10 worst
            print(f"\n📄 {gap['file']}")
            print(f"   Coverage: {gap['coverage_percent']:.1f}%")
            print(f"   Missing: {len(gap['missing_lines'])}/{gap['total_lines']} lines")

            if gap["missing_functions"]:
                print("   Untested functions:")
                for func in gap["missing_functions"][:5]:  # Show first 5
                    print(f"     - {func}")

        self._generate_test_recommendations()

    def _generate_test_recommendations(self):
        """Generate specific test creation recommendations."""
        print("\n💡 SPECIFIC TEST CREATION ACTIONS:")
        print("=" * 60)

        for gap in self.gaps[:5]:  # Top 5 priorities
            print(f"\n🎯 Priority: {gap['file']} ({gap['coverage_percent']:.1f}%)")

            # Generate specific test actions based on missing functions
            for func in gap["missing_functions"][:3]:
                print(f"   • Create test for: {func}")

            # General recommendations based on file type
            if "server" in gap["file"]:
                print("   • Add error handling tests")
                print("   • Add performance boundary tests")
            elif "client" in gap["file"]:
                print("   • Add connection failure tests")
                print("   • Add SSL/TLS scenario tests")
            elif "config" in gap["file"]:
                print("   • Add invalid config tests")
                print("   • Add edge case parsing tests")


def main():
    analyzer = CoverageGapAnalyzer()

    if analyzer.load_coverage_data():
        analyzer.analyze_gaps()
    else:
        print("❌ Could not load coverage data. Run tests with coverage first.")


if __name__ == "__main__":
    main()
