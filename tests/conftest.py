import os
from datetime import datetime


def pytest_configure(config):
    """Automatically generate timestamped HTML test reports in /reports."""
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports", "test_reports")
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_path = os.path.join(reports_dir, f"test_report_{timestamp}.html")

    # Add custom HTML report path if pytest-html is installed
    config.option.htmlpath = report_path
    config.option.self_contained_html = True

    print(f"\n🧾 Test report will be saved to: {report_path}\n")
