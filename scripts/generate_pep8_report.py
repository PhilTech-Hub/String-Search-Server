#!/usr/bin/env python3
"""
PEP 8 Compliance Report Generator
Creates detailed reports on code style compliance.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path


def generate_pep8_report():
    """Generate comprehensive PEP 8 compliance report."""

    print("📊 Generating PEP 8 Compliance Report")
    print("=" * 50)

    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {},
        "files": {},
        "common_issues": {},
        "recommendations": [],
    }

    # Find Python files
    python_files = []
    for root, dirs, files in os.walk("."):
        if any(excluded in root for excluded in ["__pycache__", ".git", "venv"]):
            continue
        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)

    report["summary"]["total_files"] = len(python_files)

    # Analyze each file
    for file_path in python_files:
        file_report = analyze_file(file_path)
        report["files"][str(file_path)] = file_report

    # Generate summary statistics
    generate_summary(report)

    # Save report
    report_path = "reports/pep8_compliance_report.json"
    Path("reports").mkdir(exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Report saved to: {report_path}")

    # Print executive summary
    print_executive_summary(report)

    return report


def analyze_file(file_path):
    """Analyze a single file for PEP 8 compliance."""
    analysis = {"line_count": 0, "long_lines": [], "issues": [], "compliance_score": 100}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        analysis["line_count"] = len(lines)

        # Check line lengths
        for i, line in enumerate(lines, 1):
            line_length = len(line.rstrip("\n\r"))
            if line_length > 100:
                analysis["long_lines"].append(
                    {"line_number": i, "length": line_length, "preview": line[:50].strip()}
                )

        # Run pycodestyle
        try:
            result = subprocess.run(
                ["pycodestyle", "--max-line-length=100", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                issues = result.stdout.strip().split("\n")
                analysis["issues"] = issues
                # Calculate compliance score (0-100)
                issue_count = len(issues)
                max_expected_issues = max(10, len(lines) // 10)  # Heuristic
                analysis["compliance_score"] = max(
                    0, 100 - (issue_count / max_expected_issues * 100)
                )

        except (subprocess.TimeoutExpired, FileNotFoundError):
            analysis["issues"] = ["Could not run pycodestyle"]

    except Exception as e:
        analysis["error"] = str(e)

    return analysis


def generate_summary(report):
    """Generate summary statistics for the report."""
    files = report["files"]

    total_issues = 0
    files_with_issues = 0
    total_long_lines = 0
    compliance_scores = []

    for file_analysis in files.values():
        total_issues += len(file_analysis.get("issues", []))
        if file_analysis.get("issues"):
            files_with_issues += 1
        total_long_lines += len(file_analysis.get("long_lines", []))
        compliance_scores.append(file_analysis.get("compliance_score", 0))

    report["summary"]["total_issues"] = total_issues
    report["summary"]["files_with_issues"] = files_with_issues
    report["summary"]["total_long_lines"] = total_long_lines
    report["summary"]["average_compliance_score"] = (
        sum(compliance_scores) / len(compliance_scores) if compliance_scores else 100
    )

    # Calculate compliance percentage
    total_files = report["summary"]["total_files"]
    compliant_files = total_files - files_with_issues
    report["summary"]["compliance_percentage"] = (
        (compliant_files / total_files) * 100 if total_files > 0 else 100
    )


def print_executive_summary(report):
    """Print a human-readable executive summary."""
    summary = report["summary"]

    print("\n" + "=" * 50)
    print("🎯 PEP 8 COMPLIANCE EXECUTIVE SUMMARY")
    print("=" * 50)

    print(f"📁 Files Analyzed: {summary['total_files']}")
    print(f"✅ Compliant Files: {summary['total_files'] - summary['files_with_issues']}")
    print(f"⚠️  Files with Issues: {summary['files_with_issues']}")
    print(f"🔧 Total Issues: {summary['total_issues']}")
    print(f"📏 Long Lines: {summary['total_long_lines']}")
    print(f"📊 Compliance Score: {summary['average_compliance_score']:.1f}%")
    print(f"🎯 Overall Compliance: {summary['compliance_percentage']:.1f}%")

    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if summary["total_issues"] > 0:
        print("  • Run: python scripts/verify_pep8_compliance.py --fix")
        print("  • Review and fix remaining issues manually")
    if summary["total_long_lines"] > 0:
        print("  • Break long lines for better readability")
    if summary["compliance_percentage"] < 90:
        print("  • Priority: Improve overall code style compliance")
    else:
        print("  • Excellent! Maintain current code quality standards")


if __name__ == "__main__":
    import os

    generate_pep8_report()
