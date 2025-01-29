import plotly.graph_objects as go
import numpy as np
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()

HTML_CONTENT_REF = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { text-align: center; }
        table { width: 50%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: center; }
        th { background-color: #f2f2f2; }
        .chart-container { margin-bottom: 40px; }
    </style>
</head>
<body>
    <h1>Test Report: Speed and Mass per Test Case</h1>
"""


def plotler(results: dict):
    logger.info(f"Generating plotly report")

    report_ts = datetime.now().strftime("%Y-%m-%d-%H-%M")
    json_filen = report_ts + "-report-fio.json"
    json_report_filep = os.path.join(
        os.path.dirname(os.getcwd()), "workspace", json_filen)

    with open(json_report_filep, "w") as f:
        json_results = json.dumps(results, indent=4)
        f.write(json_results)

    iterations_as_lst = []

    metrics = {
        "read_io_kbytes": [],
        "read_bw": [],
        "read_iops": [],
        "read_runtime": [],
        "write_io_kbytes": [],
        "write_bw": [],
        "write_iops": [],
        "write_runtime": [],
        "base_usr_cpu": [],
        "base_sys_cpu": []
    }

    devname = next(iter(results))
    dev_report = results[devname]
    for test_name, test_data in dev_report.items():

        html_filen = report_ts + '-' + test_name + '.html'
        html_report_filep = os.path.join(
            os.path.dirname(os.getcwd()), "workspace", html_filen)
        html_content = HTML_CONTENT_REF

        for iteration, iteration_data in test_data.items():
            iterations_as_lst.append(int(iteration))

            metrics['read_io_kbytes'].append(
                float(iteration_data['read']['io_kbytes']))
            metrics['read_bw'].append(float(iteration_data['read']['bw']))
            metrics['read_iops'].append(float(iteration_data['read']['iops']))
            metrics['read_runtime'].append(
                float(iteration_data['read']['runtime']))

            metrics['write_io_kbytes'].append(
                float(iteration_data['write']['io_kbytes']))
            metrics['write_bw'].append(float(iteration_data['write']['bw']))
            metrics['write_iops'].append(
                float(iteration_data['write']['iops']))
            metrics['write_runtime'].append(
                float(iteration_data['write']['runtime']))

            metrics['base_usr_cpu'].append(float(iteration_data['usr_cpu']))
            metrics['base_sys_cpu'].append(float(iteration_data['sys_cpu']))

        for metric_name, metric_data in metrics.items():
            metric_mean = np.mean(metric_data)

            # Build HTML table
            table_html = f"""
            <table>
                <tr>
                    <th>Iteration</th>
                    <th>{metric_name}</th>
                </tr>
            """

            for i in range(len(iterations_as_lst)):
                table_html += f"""
                <tr>
                    <td>{iterations_as_lst[i]}</td>
                    <td>{metric_data[i]}</td>
                </tr>
                """

            # Add mean row
            table_html += f"""
                <tr>
                    <th>Mean</th>
                    <td>{metric_mean:.2f}</td>
                </tr>
            </table>
            """

            # Create Plotly graph
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=iterations_as_lst, y=metric_data,
                                     mode='lines+markers', name=metric_name))

            # Update layout
            fig.update_layout(
                title=metric_name,
                xaxis_title="Test Iteration",
                yaxis_title="{} [Unit]".format(metric_name),
                template="plotly_white"
            )

            # Convert figure to HTML div
            div_html = fig.to_html(full_html=False, include_plotlyjs=False)

            # Append to HTML content
            html_content += f"<div class='chart-container'><h2>{test_name}</h2>{table_html}{div_html}</div>"

        # Close HTML
        html_content += """
        </body>
        </html>
        """

        # Save report
        with open(html_report_filep, "w") as f:
            f.write(html_content)
