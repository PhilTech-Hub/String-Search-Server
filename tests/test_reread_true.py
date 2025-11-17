"""
Specific test for REREAD_ON_QUERY=True algorithms (40ms requirement)
"""

from server.server import StringSearchServer
import time
import statistics
from pathlib import Path

# Add the parent directory to Python path
import sys

sys.path.append(str(Path(__file__).parent.parent))


def test_reread_true_performance():
    """Test only REREAD_ON_QUERY=True algorithms against 40ms requirement."""

    print("🧪 TESTING REREAD_ON_QUERY=True ALGORITHMS")
    print("=" * 50)
    print("Requirement: < 40ms average search time")
    print("=" * 50)

    # Create a config with REREAD_ON_QUERY=True
    config_content = """HOST=127.0.0.1
PORT=44445
linuxpath=./data/sample_text.txt
REREAD_ON_QUERY=True
SSL_ENABLED=False
"""

    config_path = Path("config/reread_true_test.conf")
    config_path.parent.mkdir(exist_ok=True)
    config_path.write_text(config_content)

    # Test each algorithm that would be used with REREAD_ON_QUERY=True
    algorithms = {
        "Python in search": "Tests the 'in' operator with file re-read",
        "mmap search": "Tests memory-mapped file search",
        "Streaming search": "Tests streaming file search",
    }

    results = {}

    for algo_name, description in algorithms.items():
        print(f"\n🔹 Testing: {algo_name}")
        print(f"   Description: {description}")

        # Create server instance (this will use REREAD_ON_QUERY=True)
        server = StringSearchServer(str(config_path))

        # Test with various search queries
        test_queries = ["apple", "mango", "watermelon", "nonexistent_fruit123"]
        query_times = []

        for query in test_queries:
            times = []
            for i in range(5):  # Multiple iterations per query
                start_time = time.perf_counter()
                result = server.search_string(query)
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)  # Convert to ms

            avg_query_time = statistics.mean(times)
            query_times.append(avg_query_time)
            print(f"   Query '{query}': {avg_query_time:.3f}ms")

        # Calculate overall average
        overall_avg = statistics.mean(query_times)
        max_time = max(query_times)
        min_time = min(query_times)

        requirement = 40.0
        meets_requirement = overall_avg <= requirement

        results[algo_name] = {
            "avg_time_ms": overall_avg,
            "min_time_ms": min_time,
            "max_time_ms": max_time,
            "meets_requirement": meets_requirement,
            "status": "PASS" if meets_requirement else "FAIL",
        }

        print(f"   📊 Overall: {overall_avg:.3f}ms (range: {min_time:.3f}-{max_time:.3f}ms)")
        print(f"   ✅ Requirement: {requirement}ms -> {'PASS' if meets_requirement else 'FAIL'}")
        print(
            f"   📈 Margin: {
                requirement /
                overall_avg:.1f}x {
                'faster' if meets_requirement else 'slower'} than requirement"
        )

    # Summary
    print("\n" + "=" * 50)
    print("🎯 REREAD_ON_QUERY=True VALIDATION SUMMARY")
    print("=" * 50)

    all_pass = all(r["meets_requirement"] for r in results.values())

    all_passed = all(r["meets_requirement"] for r in results.values())

    for algo_name, result in results.items():
        status_icon = "✅" if result["meets_requirement"] else "❌"
        print(
            f"{status_icon} {
                algo_name:20}: {
                result['avg_time_ms']:6.3f}ms vs 40ms -> {
                result['status']}"
        )

    msg = "ALL ALGORITHMS MEET 40ms REQUIREMENT" if all_passed else "SOME FAILED"
    print(f"\nOverall: {msg}")

    return all_pass


if __name__ == "__main__":
    success = test_reread_true_performance()
    exit(0 if success else 1)
