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

METRICS = {
    # I/O statistics for READ direction
    'read_io_kbytes': {
        'data': [],
        'unit': 'KB',
        'description': 'Total I/O (read) performed in KB (should match the amount of data transfered)'
    },
    'read_bw_bytes': {
        'data': [],
        'unit': 'MB/s',
        'description': 'Average bandwidth rate (read) in MB/s'
    },
    'read_iops': {
        'data': [],
        'unit': 'I/O ops',
        'description': 'Number of read *operations* done per second in IOPS'
    },
    'read_runtime': {
        'data': [],
        'unit': 'ms',
        'description': 'Runtime of the READ thread in ms'
    },

    # I/O statistics for WRITE direction
    'write_io_kbytes': {
        'data': [],
        'unit': 'KB',
        'description': 'Total I/O (write) performed in KB (should match the amount of data transfered)'
    },
    'write_bw_bytes': {
        'data': [],
        'unit': 'MB/s',
        'description': 'Average bandwidth rate (write) in MB/s'
    },
    'write_iops': {
        'data': [],
        'unit': 'I/O ops',
        'description': 'Number of write *operations* done per second in IOPS'
    },
    'write_runtime': {
        'data': [],
        'unit': 'ms',
        'description': 'Runtime of the WRITE thread in ms'
    },

    # CPU time statistics for all operations
    'base_usr_cpu': {
        'data': [],
        'unit': '% cpu time',
        'description': 'usr cpu usage - percentage of cpu time in usr space'
    },
    'base_sys_cpu': {
        'data': [],
        'unit': '% cpu time',
        'description': 'sys cpu usage - percentage of cpu time in sys space'
    },
}


def plotler(results: dict):
    logger.info(f"Generating plotly report")

    report_ts = datetime.now().strftime("%Y-%m-%d-%H-%M")
    json_filen = report_ts + "-report-fio.json"
    json_report_filep = os.path.join(
        os.path.dirname(os.getcwd()), "workspace", json_filen)

    with open(json_report_filep, "w") as f:
        json_results = json.dumps(results, indent=4)
        f.write(json_results)

    devname = next(iter(results))
    dev_report = results[devname]
    for test_name, test_data in dev_report.items():

        # Cleanup
        iterations_as_lst = []
        for _, metric_data in METRICS.items():
            metric_data['data'] = []

        html_filen = report_ts + '-' + test_name + '.html'
        html_report_filep = os.path.join(
            os.path.dirname(os.getcwd()), "workspace", html_filen)
        html_content = HTML_CONTENT_REF
        html_content += f"""
            <body>
                <h1>Test Report: {devname} - {test_name}</h1>
            """
        html_content += f"""
            <hr>
            """

        for iteration, iteration_data in test_data.items():
            iterations_as_lst.append(int(iteration))
            METRICS['read_io_kbytes']['data'].append(
                float(iteration_data['read']['io_kbytes']))
            METRICS['read_bw_bytes']['data'].append(
                float(iteration_data['read']['bw_bytes']))
            METRICS['read_iops']['data'].append(
                float(iteration_data['read']['iops']))
            METRICS['read_runtime']['data'].append(
                float(iteration_data['read']['runtime']))

            METRICS['write_io_kbytes']['data'].append(
                float(iteration_data['write']['io_kbytes']))
            METRICS['write_bw_bytes']['data'].append(
                float(iteration_data['write']['bw_bytes']))
            METRICS['write_iops']['data'].append(
                float(iteration_data['write']['iops']))
            METRICS['write_runtime']['data'].append(
                float(iteration_data['write']['runtime']))

            METRICS['base_usr_cpu']['data'].append(
                float(iteration_data['usr_cpu']))
            METRICS['base_sys_cpu']['data'].append(
                float(iteration_data['sys_cpu']))

        for metric_name, metric_data in METRICS.items():
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

            complete_name = metric_name + \
                ' [' + metric_data['unit'] + '] - ' + \
                metric_data['description']

            # Append to HTML content
            html_content += f"<div class='chart-container'><h2>{complete_name}</h2>{table_html}{div_html}</div>"
            html_content += f"""
            <hr>
            """

        # Close HTML
        html_content += """
        </body>
        </html>
        """

        # Save report
        with open(html_report_filep, "w") as f:
            f.write(html_content)
