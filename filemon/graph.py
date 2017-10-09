import sys
import threading
import time

from IPython import display
import filemon
import matplotlib.pyplot as plt
import numpy as np
import psutil


interface = "all"

class DataPlot(threading.Thread):
    
    def __init__(self, file_names, file_monitors, *args, **keywords):
        self._file_names = file_names
        self._file_monitors = file_monitors
        if not type(self._file_names) is list:
            self._file_names = [self._file_names]
        if not type(self._file_monitors) is list:
            self._file_monitors = [self._file_monitors]
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    
    def get_data_file(self, file_route):
        return filemon.FileMonitor.read_monitor_file(file_route)
                       
    def _flatten_list(self,l):
        if not type(l) is list and not type(l) is np.ndarray:
            l = [l] 
            return l
        if type(l) is np.ndarray:
            return list(l.flatten())
        flat_list = []
        for sublist in l:
            for item in sublist:
                flat_list.append(item)
        return flat_list     
    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup
        while not self.killed:
            monitor_data = {x:self.get_data_file(x) 
                            for x in self._file_monitors}
            num_plots = len(monitor_data)
            plots_per_line = 2
            plot_lines = int(np.ceil(float(num_plots) /
                                      float(plots_per_line)))
            width_inches = plots_per_line * 7.5
            height_inches = plot_lines * 5
             
            f, (axes) = plt.subplots(plot_lines, plots_per_line, sharex='col')
            axes=self._flatten_list(axes)
            f.set_size_inches(width_inches, height_inches)
            for (ax, file_name, file_monitor) in zip(axes, self._file_names,
                                                     monitor_data.keys()):
                mon_data = monitor_data[file_monitor]
                ax_percent = ax.twinx()
                ax.plot(mon_data["time_stamps"],mon_data["throughputs"])
                ax.set_title(file_name)
                ax.grid(alpha=0.5)
                ax.set_xlabel('time')
                ax.set_ylabel('bytes/s')
                
                ax_percent.plot(mon_data["time_stamps"],
                                mon_data["file_percents"],
                                linestyle="-",
                                color="red")
                ax_percent.set_ylabel('% completed"')
                ax_percent.set_ylim((0.0, 100.0))
            
            
            display.display(plt.show())
            display.clear_output(wait=True)
            # plt.show()
            time.sleep(0.5)
            
    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True

