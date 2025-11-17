"""
Performance Requirement Validation Script
Explicitly validates all performance guarantees are met.
"""

from server.server import StringSearchServer
import sys
import os
import time
import statistics

# Add the parent directory to Python path so we can import server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def validate_performance_requirements():
    """Validate all performance requirements are explicitly met."""

    print("🔍 PERFORMANCE REQUIREMENT VALIDATION")
    print("=" * 50)

    # Test configurations
    test_configs = [
        {
            "name": "STATIC_MODE",
            "config_file": "config/server_config.conf",  # Should have REREAD_ON_QUERY=False
            "requirement_ms": 0.5,
            "iterations": 1000,
        },
        {
            "name": "DYNAMIC_MODE",
            "config_file": "config/temp_dynamic.conf",  # We'll create this
            "requirement_ms": 40,
            "iterations": 100,
        },
    ]

    # Create dynamic config if needed
    with open("config/temp_dynamic.conf", "w") as f:
        f.write(
            """HOST=127.0.0.1
PORT=44445
linuxpath=./data/sample_text.txt
REREAD_ON_QUERY=True
SSL_ENABLED=False
"""
        )

    results = []

    for config in test_configs:
        print(f"\n📊 Testing {config['name']}")
        print(f"   Requirement: < {config['requirement_ms']}ms")

        try:
            server = StringSearchServer(config["config_file"])

            # Warm up
            for _ in range(10):
                server.search_string("apple")

            # Benchmark
            times = []
            for i in range(config["iterations"]):
                start = time.perf_counter()
                result = server.search_string("apple")
                end = time.perf_counter()
                times.append((end - start) * 1000)  # ms

            # Calculate statistics
            avg_time = statistics.mean(times)
            max_time = max(times)
            min_time = min(times)
            meets_requirement = avg_time < config["requirement_ms"]

            status = "✅ PASS" if meets_requirement else "❌ FAIL"
            margin = config["requirement_ms"] / avg_time if avg_time > 0 else float("inf")

            print(f"   Average Time: {avg_time:.6f}ms")
            print(f"   Min/Max: {min_time:.6f}ms / {max_time:.6f}ms")
            print(f"   Requirement: {config['requirement_ms']}ms")
            print(
                f"   Performance: {
                    margin:.1f}x {
                    'faster' if meets_requirement else 'slower'} than requirement"
            )
            print(f"   Status: {status}")

            results.append(
                {
                    "mode": config["name"],
                    "requirement_ms": config["requirement_ms"],
                    "actual_ms": avg_time,
                    "status": meets_requirement,
                    "margin": margin,
                }
            )

        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append(
                {
                    "mode": config["name"],
                    "requirement_ms": config["requirement_ms"],
                    "actual_ms": float("inf"),
                    "status": False,
                    "margin": 0,
                }
            )

    # Summary
    print("\n" + "=" * 50)
    print("🎯 VALIDATION SUMMARY")
    print("=" * 50)

    all_passed = all(r["status"] for r in results)
    overall_status = "✅ ALL REQUIREMENTS MET" if all_passed else "❌ SOME REQUIREMENTS FAILED"

    print(f"Overall Status: {overall_status}")

    for result in results:
        status_icon = "✅" if result["status"] else "❌"
        print(
            f"{status_icon} {result['mode']:15} | "
            f"Req: {result['requirement_ms']:5}ms | "
            f"Actual: {result['actual_ms']:8.4f}ms | "
            f"Margin: {result['margin']:5.1f}x"
        )

    return all_passed


if __name__ == "__main__":
    success = validate_performance_requirements()
    exit(0 if success else 1)
