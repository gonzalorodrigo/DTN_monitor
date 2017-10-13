import ntpath
import time

from filemon import FileMonitor
import filemon.graph as gr


def monitor_files(file_routes, expected_sizes, titles=None,
                  deadline_list=None, y_label="bytes/s", y_factor=None,
                  y_lim=None):
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
    thread  = gr.DataPlot(titles, file_monitors, y_label=y_label, 
                          y_factor=y_factor, y_lim=y_lim)
    thread.set_deadline_list(deadline_list)
    thread.daemon = True
    thread.start()
