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

    metrics = {
        # I/O statistics for READ direction
        # total io performed kbytes (should match the amount of data transfered, defined via --size)
        'read_io_kbytes': {'data': [], 'unit': 'KB'},
        # average bandwidth rate [MB/s]
        'read_bw_bytes': {'data': [], 'unit': 'MB/s'},
        # iops (number of read/write *operations* done per second. Should be correlated
        # somehow with the iodepth parameter)
        'read_iops': {'data': [], 'unit': 'I/O ops'},
        # runtime of the thread [ms]
        'read_runtime': {'data': [], 'unit': 'ms'},

        # I/O statistics for WRITE direction
        'write_io_kbytes': {'data': [], 'unit': 'KB'},
        'write_bw_bytes': {'data': [], 'unit': 'MB/s'},
        'write_iops': {'data': [], 'unit': 'I/O ops'},
        'write_runtime': {'data': [], 'unit': 'ms'},

        # CPU time statistics for all operations
        # usr cpu usage [% of cpu time in usr space]
        'base_usr_cpu': {'data': [], 'unit': '% cpu time'},
        # sys cpu usage [% of cpu time in sys space]
        'base_sys_cpu': {'data': [], 'unit': '% cpu time'},
    }

    devname = next(iter(results))
    dev_report = results[devname]
    for test_name, test_data in dev_report.items():

        # Cleanup
        iterations_as_lst = []
        for metric in metrics:
            metric['data'] = []

        html_filen = report_ts + '-' + test_name + '.html'
        html_report_filep = os.path.join(
            os.path.dirname(os.getcwd()), "workspace", html_filen)
        html_content = HTML_CONTENT_REF
        html_content += f"""
            <body>
                <h1>Test Report: {devname} - {test_name}</h1>
            """

        for iteration, iteration_data in test_data.items():
            iterations_as_lst.append(int(iteration))
            metrics['read_io_kbytes']['data'].append(
                float(iteration_data['read']['io_kbytes']))
            metrics['read_bw_bytes']['data'].append(
                float(iteration_data['read']['bw_bytes']))
            metrics['read_iops']['data'].append(
                float(iteration_data['read']['iops']))
            metrics['read_runtime']['data'].append(
                float(iteration_data['read']['runtime']))

            metrics['write_io_kbytes']['data'].append(
                float(iteration_data['write']['io_kbytes']))
            metrics['write_bw_bytes']['data'].append(
                float(iteration_data['write']['bw_bytes']))
            metrics['write_iops']['data'].append(
                float(iteration_data['write']['iops']))
            metrics['write_runtime']['data'].append(
                float(iteration_data['write']['runtime']))

            metrics['base_usr_cpu']['data'].append(
                float(iteration_data['usr_cpu']))
            metrics['base_sys_cpu']['data'].append(
                float(iteration_data['sys_cpu']))

        for metric_name, metric_data in metrics.items():
            metric_mean = np.mean(metric_data['data'])

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
                    <td>{metric_data['data'][i]}</td>
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
            fig.add_trace(go.Scatter(x=iterations_as_lst, y=metric_data['data'],
                                     mode='lines+markers', name=metric_name))

            # Update layout
            fig.update_layout(
                title=metric_name,
                xaxis_title="Test Iteration",
                yaxis_title="{} [{}]".format(metric_name, metric_data['unit']),
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
