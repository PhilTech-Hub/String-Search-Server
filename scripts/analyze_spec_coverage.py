#!/usr/bin/env python3
"""
SPECIFICATION-BASED TEST COVERAGE ANALYSIS
Analyzes test coverage against the exact String Search Server specification requirements.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set


class SpecificationCoverageAnalyzer:
    def __init__(self):
        self.spec_requirements = self._load_specification_requirements()
        self.test_coverage = {}
        self.missing_tests = {}

    def _load_specification_requirements(self) -> Dict[str, List[str]]:
        """Load all specification requirements as testable items."""
        return {
            "server_core": [
                "binds_port_and_listens",
                "handles_unlimited_concurrent_connections",
                "receives_string_in_cleartext",
                "reads_config_file_for_file_path",
                "finds_linuxpath_config_line",
                "opens_file_from_config_path",
                "searches_full_string_match_only",
                "no_partial_matches_accepted",
                "responds_string_exists_or_not_found",
                "adds_newline_to_response",
                "uses_multithreading_for_parallel_requests",
                "works_on_linux",
                "handles_files_up_to_250k_rows",
                "meets_40ms_execution_time_reread_true",
                "meets_0.5ms_execution_time_reread_false",
                "strips_null_bytes_from_payload",
                "max_payload_size_1024_bytes",
            ],
            "reread_functionality": [
                "reread_on_query_true_reloads_file",
                "reread_on_query_false_caches_file",
                "handles_microsecond_file_changes",
                "performance_40ms_with_reread_true",
                "performance_0.5ms_with_reread_false",
            ],
            "logging_output": [
                "shows_debug_logs_on_tcp",
                "includes_search_query_in_logs",
                "includes_requesting_ip_in_logs",
                "includes_execution_time_in_logs",
                "includes_timestamps_in_logs",
                "marks_logs_with_debug_prefix",
            ],
            "performance_benchmarking": [
                "tests_5_different_search_algorithms",
                "compares_algorithm_performance",
                "generates_human_readable_report",
                "includes_performance_table",
                "includes_performance_chart",
                "tests_10000_to_1000000_lines",
                "tests_queries_per_second_limits",
                "documents_software_limitations",
            ],
            "daemon_operations": [
                "runs_as_linux_daemon_service",
                "has_clear_installation_instructions",
                "handles_service_lifecycle",
            ],
            "security_features": [
                "protects_against_buffer_overflows",
                "implements_ssl_authentication",
                "supports_self_signed_certificates",
                "supports_psk_authentication",
                "ssl_configurable_true_false",
                "input_validation_sanitization",
                "handles_malicious_inputs",
            ],
            "code_quality": [
                "pep8_compliant",
                "pep20_compliant",
                "statically_typed",
                "comprehensive_docstrings",
                "professional_packaging",
                "robust_exception_handling",
                "intelligent_error_messages",
            ],
            "testing_requirements": [
                "unit_tests_cover_all_functionalities",
                "tests_different_execution_times",
                "tests_different_file_sizes",
                "tests_queries_per_second_limits",
                "tests_correct_workflow_all_paths",
                "tests_all_exceptions_edge_cases",
                "uses_pytest_framework",
                "no_hardcoded_paths_in_tests",
                "includes_test_data_in_tests_dir",
                "pytest_can_collect_and_run_tests",
            ],
            "client_implementation": [
                "includes_client_py_for_testing",
                "client_can_connect_to_server",
                "client_can_send_queries",
                "client_can_receive_responses",
                "client_handles_ssl_if_enabled",
            ],
            "documentation_packaging": [
                "includes_speed_report_pdf",
                "includes_requirements_txt",
                "includes_installation_instructions",
                "code_is_standalone_complete",
                "proper_file_naming_conventions",
                "no_unnecessary_files_in_zip",
                "no_absolute_paths_in_tests",
            ],
        }

    def discover_existing_tests(self) -> None:
        """Discover all test files and map to specification requirements."""
        test_dir = Path("tests")
        test_files = list(test_dir.glob("test_*.py")) + list(test_dir.glob("*_test.py"))

        print("🔍 DISCOVERED TEST FILES:")
        for test_file in test_files:
            print(f"   📄 {test_file.name}")
            self._analyze_test_file(test_file)

    def _analyze_test_file(self, test_file: Path) -> None:
        """Analyze a single test file and map to specification requirements."""
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read().lower()

            # Map test content to specification requirements
            for category, requirements in self.spec_requirements.items():
                for requirement in requirements:
                    if self._matches_requirement(content, requirement):
                        if category not in self.test_coverage:
                            self.test_coverage[category] = set()
                        self.test_coverage[category].add(requirement)

        except Exception as e:
            print(f"   ❌ Error analyzing {test_file}: {e}")

    def _matches_requirement(self, content: str, requirement: str) -> bool:
        """Check if test content matches a specification requirement."""
        # Convert requirement to search patterns
        patterns = [
            requirement,
            requirement.replace("_", " "),
            requirement.replace("_", ""),
            "test_" + requirement,
            requirement + "_test",
        ]

        for pattern in patterns:
            if pattern in content:
                return True
        return False

    def generate_coverage_report(self) -> None:
        """Generate comprehensive coverage report against specification."""
        print("\n" + "=" * 80)
        print("🎯 SPECIFICATION TEST COVERAGE REPORT")
        print("=" * 80)

        total_requirements = sum(len(reqs) for reqs in self.spec_requirements.values())
        covered_requirements = sum(len(reqs) for reqs in self.test_coverage.values())
        coverage_percentage = (covered_requirements / total_requirements) * 100

        print(f"\n📊 OVERALL COVERAGE: {coverage_percentage:.1f}%")
        print(f"   ✅ Covered: {covered_requirements}/{total_requirements} requirements")

        # Detailed category breakdown
        print("\n📈 COVERAGE BY SPECIFICATION CATEGORY:")
        print("-" * 80)

        for category, requirements in self.spec_requirements.items():
            covered = len(self.test_coverage.get(category, set()))
            total = len(requirements)
            category_coverage = (covered / total) * 100 if total > 0 else 0

            # Status indicator
            if category_coverage >= 90:
                status = "✅ EXCELLENT"
            elif category_coverage >= 70:
                status = "⚠️  GOOD"
            elif category_coverage >= 50:
                status = "🔶 FAIR"
            else:
                status = "❌ POOR"

            print(
                f"\n{
                    category.upper():25} {
                    status:12} {
                    category_coverage:5.1f}% ({
                    covered:2d}/{
                        total:2d})"
            )

            # Show missing requirements for poor coverage categories
            if category_coverage < 80:
                covered_set = self.test_coverage.get(category, set())
                missing = [req for req in requirements if req not in covered_set]
                if missing:
                    print("   Missing tests:")
                    for miss in missing[:5]:  # Show first 5 missing
                        print(f"     - {miss}")
                    if len(missing) > 5:
                        print(f"     ... and {len(missing) - 5} more")

    def identify_critical_missing_tests(self) -> None:
        """Identify critical specification requirements that are missing tests."""
        print("\n🚨 CRITICAL MISSING TEST COVERAGE:")
        print("-" * 80)

        critical_categories = [
            "server_core",
            "security_features",
            "performance_benchmarking",
            "testing_requirements",
        ]

        for category in critical_categories:
            if category in self.spec_requirements:
                covered = len(self.test_coverage.get(category, set()))
                total = len(self.spec_requirements[category])

                if covered < total:
                    missing_count = total - covered
                    print(f"\n❌ {category.upper()}: {missing_count} missing tests")

                    covered_set = self.test_coverage.get(category, set())
                    missing_reqs = [
                        req for req in self.spec_requirements[category] if req not in covered_set
                    ]

                    for req in missing_reqs:
                        print(f"   - {req}")

    def generate_test_creation_plan(self) -> None:
        """Generate a prioritized plan for creating missing tests."""
        print("\n💡 TEST CREATION PRIORITY PLAN:")
        print("-" * 80)

        priority_plan = {
            "HIGH PRIORITY": [
                "Create performance benchmark tests for 40ms/0.5ms requirements",
                "Implement SSL/TLS authentication tests",
                "Create security tests for buffer overflow protection",
                "Add concurrent connection stress tests",
                "Create file change detection tests for REREAD_ON_QUERY",
            ],
            "MEDIUM PRIORITY": [
                "Add comprehensive error handling tests",
                "Create configuration file parsing tests",
                "Implement daemon/service lifecycle tests",
                "Add payload size and null byte handling tests",
            ],
            "LOW PRIORITY": [
                "Create documentation validation tests",
                "Add packaging and deployment tests",
                "Implement code quality compliance tests",
            ],
        }

        for priority, tasks in priority_plan.items():
            print(f"\n{priority}:")
            for task in tasks:
                print(f"   • {task}")


if __name__ == "__main__":
    analyzer = SpecificationCoverageAnalyzer()
    analyzer.discover_existing_tests()
    analyzer.generate_coverage_report()
    analyzer.identify_critical_missing_tests()
    analyzer.generate_test_creation_plan()
