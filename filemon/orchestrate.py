"""Module to coordinate monitoring and plotting for multiple files."""

import ntpath
import time

from filemon import FileMonitor
import filemon.graph as gr
import filemon.rest_reporter as rr


def monitor_files(file_routes, expected_sizes, titles=None,
                  deadline_list=None, y_label="bytes/s", y_factor=None,
                  y_lim=None, rest_reporting=False,
                  hostname="127.0.0.1", port=5000,
                  file_ids=None):
    """ Starts file monitors for a number of files and then draws plots on the
    obtained measuring samples. Argumens are list that must be of the same
    size and which items in the same position correspond to the monitoring of
    the same file.
    
    It's execution is non blocking.
    
    Args:
      file_routes: list of strings pointing to the files to be monitored.
      expected_sizes: list of integers describing the size of the moniored files
        in bytes.
    titles: list of strings to be used as titles of the subplots..
    deadeline_list: list of time objects indicating the timestamp of the
      deadlines of each file.
    y_label: string to be used as y_label in the throughput axis of each
      subplot.
    y_factor: if set to a flaot, all throughput data will be multiplied by this
      float before plotting.
    y_lim: if set to a tuple (y_min, y_max), it will be used as the limits of
      the y_axis of all the subplotes. 
    """
    file_monitors = [] 
    for (file_route, i, expected_size) in zip(file_routes,
                                              range(len(file_routes)),
                                              expected_sizes):
        file_monitor = "monitor.{}.{}".format(i,ntpath.basename(file_route))
        fm = FileMonitor()
        fm.monitor_file_name_async(file_route, expected_size,
                                        file_monitor)
        file_monitors.append(file_monitor)
    
    time.sleep(1.0)
    if file_routes is None:
        titles=file_routes
    if not rest_reporting:
        thread  = gr.DataPlot(titles, file_monitors, y_label=y_label, 
                          y_factor=y_factor, y_lim=y_lim)
    else:
        if file_ids:
            file_id_dict={x:y for (x,y) in zip(file_monitors, file_ids)}
        thread  = rr.RestReporter(titles, file_monitors, y_label=y_label, 
                          y_factor=y_factor, y_lim=y_lim)
        thread.set_rest_server_ip(hostname, port)
        thread.set_files_rest_ids(file_id_dict)
        
    thread.set_deadline_list(deadline_list)
    thread.daemon = True
    thread.start()
