#!/usr/bin/env python3
"""
CI COVERAGE CHECK
Fail the build if coverage drops below thresholds.
"""

import subprocess
import json
import sys
from pathlib import Path


def check_coverage_thresholds():
    """Check if coverage meets minimum thresholds."""

    # Generate coverage report
    result = subprocess.run(["python", "-m", "coverage", "json"], capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Failed to generate coverage report")
        return False

    if not Path("coverage.json").exists():
        print("❌ Coverage file not found")
        return False

    with open("coverage.json", "r") as f:
        coverage_data = json.load(f)

    # Check overall coverage
    overall = coverage_data.get("totals", {}).get("percent_covered", 0)
    print(f"📊 Overall Coverage: {overall:.1f}%")

    # Check module-specific coverage
    thresholds = {
        "server/": 85,
        "client/": 80,
        "server/config.py": 90,
        "server/server.py": 85,
        "client/client.py": 80,
    }

    all_passed = True

    for module_pattern, threshold in thresholds.items():
        module_coverage = 0
        module_files = 0

        for file_path, file_data in coverage_data["files"].items():
            if module_pattern in file_path:
                file_cov = file_data.get("summary", {}).get("percent_covered", 0)
                module_coverage += file_cov
                module_files += 1

        if module_files > 0:
            avg_coverage = module_coverage / module_files
            status = "✅" if avg_coverage >= threshold else "❌"
            print(f"{status} {module_pattern}: {avg_coverage:.1f}% (threshold: {threshold}%)")

            if avg_coverage < threshold:
                all_passed = False

    if overall < 80:
        print(f"❌ Overall coverage {overall:.1f}% below 80% threshold")
        all_passed = False

    return all_passed


if __name__ == "__main__":
    if check_coverage_thresholds():
        print("🎉 All coverage thresholds met!")
        sys.exit(0)
    else:
        print("🚨 Some coverage thresholds failed!")
        sys.exit(1)
