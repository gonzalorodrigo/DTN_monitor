import ntpath
import time

from filemon import FileMonitor
import filemon.graph as gr


def monitor_files(file_routes, expected_sizes, titles=None):
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
    thread  = gr.DataPlot(titles, file_monitors)
    thread.daemon = True
    thread.start()
