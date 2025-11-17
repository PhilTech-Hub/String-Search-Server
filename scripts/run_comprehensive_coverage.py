#!/usr/bin/env python3
"""
COMPREHENSIVE COVERAGE TEST RUNNER
Runs all tests with detailed coverage analysis and generates reports.
"""

import subprocess
import sys
import os
import json
from pathlib import Path
import webbrowser


class CoverageTestRunner:
    def __init__(self):
        self.coverage_data = {}
        self.test_results = {}

    def run_unit_test_coverage(self):
        """Run unit tests with coverage analysis."""
        print("🧪 RUNNING UNIT TEST COVERAGE...")
        print("=" * 60)

        commands = [
            # Basic coverage
            [
                "python",
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--cov=server",
                "--cov=client",
                "--cov-report=term-missing",
                "--cov-report=html:coverage_html/unit",
            ],
            # Coverage with branch analysis
            [
                "python",
                "-m",
                "pytest",
                "tests/",
                "--cov=server",
                "--cov=client",
                "--cov-branch",
                "--cov-report=html:coverage_html/unit_branch",
            ],
            # Specific module coverage
            [
                "python",
                "-m",
                "pytest",
                "tests/test_server.py",
                "tests/test_client.py",
                "--cov=server.server",
                "--cov=client.client",
                "--cov-report=html:coverage_html/core_modules",
            ],
        ]

        for cmd in commands:
            print(f"\n📋 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Success")
            else:
                print(f"❌ Failed: {result.stderr}")

    def run_performance_coverage(self):
        """Run performance tests with coverage."""
        print("\n⚡ RUNNING PERFORMANCE TESTS WITH COVERAGE...")
        print("=" * 60)

        perf_tests = [
            "tests/test_performance_specification.py",
            "tests/test_benchmark_search_algorithms.py",
            "tests/test_reread_true.py",
        ]

        for test_file in perf_tests:
            if Path(test_file).exists():
                cmd = [
                    "python",
                    "-m",
                    "pytest",
                    test_file,
                    "-v",
                    "--cov=server",
                    "--cov-append",
                    "--benchmark-only",
                ]
                print(f"📊 Running performance coverage: {test_file}")
                subprocess.run(cmd)

    def run_security_coverage(self):
        """Run security tests with coverage."""
        print("\n🔒 RUNNING SECURITY TESTS WITH COVERAGE...")
        print("=" * 60)

        # Look for security-related tests
        security_patterns = ["security", "ssl", "auth", "buffer", "overflow"]
        security_tests = []

        for test_file in Path("tests").glob("test_*.py"):
            content = test_file.read_text().lower()
            if any(pattern in content for pattern in security_patterns):
                security_tests.append(str(test_file))

        if security_tests:
            cmd = (
                ["python", "-m", "pytest"]
                + security_tests
                + ["-v", "--cov=server", "--cov-append", "--cov-report=html:coverage_html/security"]
            )
            print(f"🔐 Running security tests: {', '.join(security_tests)}")
            subprocess.run(cmd)
        else:
            print("⚠️  No security-specific tests found")

    def generate_missing_tests_report(self):
        """Generate report of untested code."""
        print("\n📋 GENERATING MISSING TESTS REPORT...")
        print("=" * 60)

        # Get coverage data
        cmd = ["python", "-m", "coverage", "json", "-o", "coverage.json"]
        subprocess.run(cmd)

        if Path("coverage.json").exists():
            with open("coverage.json", "r") as f:
                coverage_data = json.load(f)

            self._analyze_missing_coverage(coverage_data)

    def _analyze_missing_coverage(self, coverage_data):
        """Analyze missing coverage and generate recommendations."""
        missing_tests = []

        for file_path, file_data in coverage_data["files"].items():
            missing_lines = file_data.get("missing_lines", [])
            if missing_lines and "test" not in file_path:
                missing_tests.append(
                    {
                        "file": file_path,
                        "missing_lines": missing_lines,
                        "executable_lines": file_data.get("executable_lines", 0),
                        "coverage_percent": file_data.get("summary", {}).get("percent_covered", 0),
                    }
                )

        # Sort by worst coverage first
        missing_tests.sort(key=lambda x: x["coverage_percent"])

        print("\n🚨 FILES WITH POOR COVERAGE:")
        for file_info in missing_tests[:10]:  # Top 10 worst
            if file_info["coverage_percent"] < 80:
                print(f"❌ {file_info['file']}: {file_info['coverage_percent']:.1f}%")

        # Generate test recommendations
        self._generate_test_recommendations(missing_tests)

    def _generate_test_recommendations(self, missing_tests):
        """Generate specific test creation recommendations."""
        print("\n💡 TEST CREATION RECOMMENDATIONS:")

        recommendations = []
        for file_info in missing_tests:
            if file_info["coverage_percent"] < 80:
                file_path = file_info["file"]
                if "server" in file_path:
                    rec = f"Create comprehensive tests for {file_path}"
                    recommendations.append(rec)
                elif "client" in file_path:
                    rec = f"Add client functionality tests for {file_path}"
                    recommendations.append(rec)
                elif "config" in file_path:
                    rec = f"Implement configuration parsing tests for {file_path}"
                    recommendations.append(rec)

        for i, rec in enumerate(recommendations[:10], 1):
            print(f"  {i}. {rec}")

    def run_static_analysis(self):
        """Run static analysis tools."""
        print("\n🔍 RUNNING STATIC ANALYSIS...")
        print("=" * 60)

        tools = [
            ["python", "-m", "mypy", "server/", "client/", "--ignore-missing-imports"],
            ["python", "-m", "pylint", "server/", "client/"],
            ["python", "-m", "bandit", "-r", "server/", "-f", "txt"],
        ]

        for tool in tools:
            print(f"\n🔧 Running: {' '.join(tool)}")
            result = subprocess.run(tool, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Static analysis passed")
            else:
                print(f"⚠️  Issues found:\n{result.stdout}")

    def generate_final_report(self):
        """Generate final coverage report."""
        print("\n📊 GENERATING FINAL COVERAGE REPORT...")
        print("=" * 60)

        # Generate comprehensive report
        subprocess.run(["python", "-m", "coverage", "report", "--show-missing", "--skip-covered"])

        # Generate HTML report
        subprocess.run(["python", "-m", "coverage", "html", "--directory=coverage_html/final"])

        print("\n🎯 COVERAGE SUMMARY:")
        print("✅ Unit tests coverage generated")
        print("✅ Performance tests coverage generated")
        print("✅ Security tests coverage generated")
        print("✅ Missing tests analysis completed")
        print("✅ Static analysis completed")
        print("📁 HTML reports available in: coverage_html/")

        # Try to open the report
        try:
            webbrowser.open("coverage_html/final/index.html")
        except BaseException:
            print("🌐 Open coverage_html/final/index.html in your browser to view the report")


def main():
    runner = CoverageTestRunner()

    try:
        runner.run_unit_test_coverage()
        runner.run_performance_coverage()
        runner.run_security_coverage()
        runner.run_static_analysis()
        runner.generate_missing_tests_report()
        runner.generate_final_report()

        print("\n🎉 COMPREHENSIVE COVERAGE TESTING COMPLETED!")

    except Exception as e:
        print(f"❌ Error during coverage testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
