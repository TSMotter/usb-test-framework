import pytest
import os
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()


@pytest.fixture(scope="class")
def html_report_dd():
    logger.info(f"Setting up html_report_dd object")
    results = []

    yield results

    logger.info(f"Creating html_report_dd...")
    report_file = "html_report_dd.html"

    if os.path.exists(report_file):
        os.remove(f"{report_file}")

    with open(report_file, "w") as f:
        f.write("<html><head><title>USB Test Report</title></head><body>\n")
        f.write("<h1>USB Test Report</h1>\n")
        f.write("<table border='1'>\n")
        f.write(
            "<tr><th>Iteration</th><th>Write Time (s)</th><th>Read Time (s)</th><th>Hash Match</th></tr>\n")

        for result in results:
            color = "green" if result["hash_match"] else "red"
            f.write(
                f"<tr><td>{result['iteration']}</td>"
                f"<td>{result['write_duration']:.2f}</td>"
                f"<td>{result['read_duration']:.2f}</td>"
                f"<td style='color:{color};'>{'PASS' if result['hash_match'] else 'FAIL'}</td></tr>\n"
            )

        f.write("</table>\n</body></html>\n")


@pytest.fixture(scope="class")
def report_fio():
    logger.info(f"Setting up report_fio object")
    results = {}

    yield results

    logger.info(f"Creating report_fio...")
    json_results = json.dumps(results, indent=4)
    logger.info(f"{json_results}")

    device_report = json_results[0]
    for testcase in device_report:
        for iteration in testcase:
            base_usr_cpu = iteration['usr_cpu']
            base_sys_cpu = iteration['sys_cpu']
            read_dict = iteration['read']
            write_dict = iteration['write']

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    report_file = timestamp + "-report-fio.json"
    if os.path.exists(report_file):
        os.remove(f"{report_file}")
    with open(report_file, "w") as f:
        f.write(json_results)
