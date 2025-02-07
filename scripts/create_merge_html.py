import plotly.graph_objects as go
import numpy as np
import json
import logging
from datetime import datetime
import os
import sys
import copy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers.plotly import HTML_CONTENT_REF, METRICS


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()


def main(file_a: str, file_b: str):
    try:
        metrics_a = copy.deepcopy(METRICS)
        metrics_b = copy.deepcopy(METRICS)
        content_dict_a = {}
        content_dict_b = {}

        html_filen = 'merged-' + os.path.basename(file_a) + '-' + os.path.basename(file_b) + '.html'
        logger.info(f"Will be creating {html_filen}")

        file_a = os.path.join(os.getcwd(), file_a)
        file_b = os.path.join(os.getcwd(), file_b)
        logger.info(f"Will try to open {file_a}")
        logger.info(f"Will try to open {file_b}")

        with open(file_a, 'r') as f_a, open(file_b, 'r') as f_b:
            content_dict_a = json.load(f_a)
            content_dict_b = json.load(f_b)

        # Use file_a as 'reference'
        devname_a = next(iter(content_dict_a))
        dev_report_a = content_dict_a[devname_a]
        devname_b = next(iter(content_dict_b))
        dev_report_b = content_dict_b[devname_b]

        for (test_name_a, test_data_a), (_, test_data_b) in zip(dev_report_a.items(), dev_report_b.items()):
            # Cleanup
            iterations_as_lst = []
            for _, metric_data in metrics_a.items():
                metric_data['data'] = []
            for _, metric_data in metrics_b.items():
                metric_data['data'] = []

            html_content = HTML_CONTENT_REF
            html_content += f"""
                <body>
                    <h1>Test Report: {devname_a} merged with {devname_b} - {test_name_a}</h1>
                """
            html_content += f"""
                <hr>
                """

            for (iteration_a, iteration_data_a), (_, iteration_data_b) in zip(test_data_a.items(), test_data_b.items()):
                iterations_as_lst.append(int(iteration_a))
                metrics_a['read_io_kbytes']['data'].append(
                    float(iteration_data_a['read']['io_kbytes']))
                metrics_a['read_bw_bytes']['data'].append(
                    float(iteration_data_a['read']['bw_bytes']))
                metrics_a['read_iops']['data'].append(
                    float(iteration_data_a['read']['iops']))
                metrics_a['read_runtime']['data'].append(
                    float(iteration_data_a['read']['runtime']))

                metrics_a['write_io_kbytes']['data'].append(
                    float(iteration_data_a['write']['io_kbytes']))
                metrics_a['write_bw_bytes']['data'].append(
                    float(iteration_data_a['write']['bw_bytes']))
                metrics_a['write_iops']['data'].append(
                    float(iteration_data_a['write']['iops']))
                metrics_a['write_runtime']['data'].append(
                    float(iteration_data_a['write']['runtime']))

                metrics_a['base_usr_cpu']['data'].append(
                    float(iteration_data_a['usr_cpu']))
                metrics_a['base_sys_cpu']['data'].append(
                    float(iteration_data_a['sys_cpu']))

                metrics_b['read_io_kbytes']['data'].append(
                    float(iteration_data_b['read']['io_kbytes']))
                metrics_b['read_bw_bytes']['data'].append(
                    float(iteration_data_b['read']['bw_bytes']))
                metrics_b['read_iops']['data'].append(
                    float(iteration_data_b['read']['iops']))
                metrics_b['read_runtime']['data'].append(
                    float(iteration_data_b['read']['runtime']))

                metrics_b['write_io_kbytes']['data'].append(
                    float(iteration_data_b['write']['io_kbytes']))
                metrics_b['write_bw_bytes']['data'].append(
                    float(iteration_data_b['write']['bw_bytes']))
                metrics_b['write_iops']['data'].append(
                    float(iteration_data_b['write']['iops']))
                metrics_b['write_runtime']['data'].append(
                    float(iteration_data_b['write']['runtime']))

                metrics_b['base_usr_cpu']['data'].append(
                    float(iteration_data_b['usr_cpu']))
                metrics_b['base_sys_cpu']['data'].append(
                    float(iteration_data_b['sys_cpu']))

            for (metric_name_a, metric_data_a), (metric_name_b, metric_data_b) in zip(metrics_a.items(), metrics_b.items()):
                metric_mean_a = np.mean(metric_data_a['data'])
                metric_mean_b = np.mean(metric_data_b['data'])

                complete_metric_name_a = f"{metric_name_a} ({devname_a})"
                complete_metric_name_b = f"{metric_name_b} ({devname_b})"
                # User 'a' as reference
                metric_name_ref = copy.deepcopy(metric_name_a)
                metric_data_ref = copy.deepcopy(metric_data_a)

                # Build HTML table
                table_html = f"""
                <table>
                    <tr>
                        <th>Iteration</th>
                        <th>{complete_metric_name_a}</th>
                        <th>{complete_metric_name_b}</th>
                    </tr>
                """

                for i in range(len(iterations_as_lst)):
                    table_html += f"""
                    <tr>
                        <td>{iterations_as_lst[i]}</td>
                        <td>{metric_data_a['data'][i]}</td>
                        <td>{metric_data_b['data'][i]}</td>
                    </tr>
                    """

                # Add mean row
                table_html += f"""
                    <tr>
                        <th>Mean</th>
                        <td>{metric_mean_a:.2f}</td>
                        <td>{metric_mean_b:.2f}</td>
                    </tr>
                </table>
                """

                # Create Plotly graph
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=iterations_as_lst, y=metric_data_a['data'],
                                         mode='lines+markers', name=devname_a))
                fig.add_trace(go.Scatter(x=iterations_as_lst, y=metric_data_b['data'],
                                         mode='lines+markers', name=devname_b))

                # Update layout
                fig.update_layout(
                    title=metric_name_ref,
                    xaxis_title="Test Iteration",
                    yaxis_title="{} [{}]".format(
                        metric_name_ref, metric_data_ref['unit']),
                    template="plotly_white"
                )

                # Convert figure to HTML div
                div_html = fig.to_html(full_html=False, include_plotlyjs=False)

                complete_name = metric_name_ref + \
                    ' [' + metric_data_ref['unit'] + '] - ' + \
                    metric_data_ref['description']

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
            with open(html_filen, "w") as f:
                f.write(html_content)

    except FileNotFoundError as e:
        logger.warning(f"Error: {e}")
    except Exception as e:
        logger.warning(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info(f"Usage: {sys.argv[0]} <file_a> <file_b>")
        sys.exit(1)

    file_a = sys.argv[1]
    file_b = sys.argv[2]
    main(file_a, file_b)
