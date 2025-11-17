#!/usr/bin/env python3
"""
Generate Performance Benchmark Report
"""
import subprocess
import sys
import json
from datetime import datetime


def generate_performance_report():
    """Run performance tests and generate report"""

    print("🔍 Running Performance Benchmarks...")
    print("=" * 50)

    # Run performance tests
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/performance_benchmarks.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )

    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "performance_requirement": "Average execution time < 40ms for REREAD_ON_QUERY=True",
        "tests_executed": True,
        "output": result.stdout,
        "return_code": result.returncode,
    }

    # Save report
    with open("reports/performance_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("📊 Performance Report Generated:")
    print("  - File: reports/performance_report.json")
    print(f"  - Status: {'PASS' if result.returncode == 0 else 'FAIL'}")

    return result.returncode == 0


if __name__ == "__main__":
    success = generate_performance_report()
    sys.exit(0 if success else 1)
