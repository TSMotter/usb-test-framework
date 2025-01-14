import pytest
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()

@pytest.fixture(scope="class")
def html_report():
    logger.info(f"Setting up html_report object")
    results = []

    yield results

    logger.info(f"Creating html_report...")
    report_file = "usb_test_report.html"

    if os.path.exists(report_file):
        os.remove(f"{report_file}")

    with open(report_file, "w") as f:
        f.write("<html><head><title>USB Test Report</title></head><body>\n")
        f.write("<h1>USB Test Report</h1>\n")
        f.write("<table border='1'>\n")
        f.write("<tr><th>Iteration</th><th>Write Time (s)</th><th>Read Time (s)</th><th>Hash Match</th></tr>\n")

        for result in results:
            color = "green" if result["hash_match"] else "red"
            f.write(
                f"<tr><td>{result['iteration']}</td>"
                f"<td>{result['write_duration']:.2f}</td>"
                f"<td>{result['read_duration']:.2f}</td>"
                f"<td style='color:{color};'>{'PASS' if result['hash_match'] else 'FAIL'}</td></tr>\n"
            )

        f.write("</table>\n</body></html>\n")