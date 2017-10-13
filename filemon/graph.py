import sys
import threading
import time

from IPython import display
import filemon
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import psutil


interface = "all"

class DataPlot(threading.Thread):
    """ Class to plot data from multiple file monitors with matplotlib.
    It creates an individual subplot per monitoring file. In each subplot,
    it plots two series: data throughput (left y-axis),  completion percentage
    (right y-axis). The Subplots data is refreshed periodically. If deadline
    is set, it is represented as a vertical line.
    
    To use
    - Create DataPlot object.
    - Run thread.start()
    """
    
    def __init__(self, file_names, file_monitors, y_label="bytes/s",
                 y_factor=None, y_lim=None, refresh_rate=0.5,
                 *args, **keywords):
        """ Object Creation. The objet works with lists of file names, 
        monitor files, and deadlines. Elements in the same position of each
        list correspond to the same individual plot. 
         
        Args:
          file_names: List of strings to be used as titles of each plot.
          file_monitors: list of strings poiting to the location of 
            the monitoring files to be read for the plots.
          y_label: string to be used as y_label in each plot.
          y_factor: if set to a float, throughput values will be multoplied by
            y_factor before plotting.
          y_lim: if set to tuple(min, max), all y-axes of all subplots will
            use this limits.
          regresh_rate: float seconds between to plot refreshes.  
        """
        self._file_names = file_names
        self._file_monitors = file_monitors
        if not type(self._file_names) is list:
            self._file_names = [self._file_names]
        if not type(self._file_monitors) is list:
            self._file_monitors = [self._file_monitors]
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False
        self._deadline = None
        self._deadline_list = None
        self._y_label = y_label
        self._y_factor = y_factor
        self._y_lim = y_lim
        self._refresh_rate=refresh_rate
    
    def set_deadline(self, deadline):
        """ Sets the same deadline for all subplots.
        Args:
          deadline: time object.
        """
        self._deadline=deadline
    
    def set_deadline_list(self, deadline_list):
        """ Sets individual deadlines for each subplot.+
        Args:
          deadline_list: list of time objects representing the deadlines for
            the plots corresponding to each monitoring file.
        """
        self._deadline_list=deadline_list


    def start(self):
        """ Starts the plotting in a subthread. It is non blocking."""
        self.__run_backup = self.run
        self.run = self.__run
        self._start_time=time.time()
        threading.Thread.start(self)
        

    
    def get_data_file(self, file_route):
        """ Returns the data of the file_route a dictionary of lists."""
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
        """ Main plotting action"""
        
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup
        
        x_lim=None
        """ Sets the same x_lim for all subplots so the difference in deadlines
        for all plots can be observed."""
        if (self._deadline_list):
            x_max = max([(deadline-self._start_time)*0.10+deadline
                         for deadline in self._deadline_list])
            x_lim = (self._start_time, x_max)

        while not self.killed:
            """ Reads data """
            monitor_data = [self.get_data_file(x) 
                            for x in self._file_monitors]
            
            """ Calculates the plot disposition depending on the number of
            plots."""
            num_plots = len(monitor_data)
            plots_per_line = 2
            plot_lines = int(np.ceil(float(num_plots) /
                                      float(plots_per_line)))
            width_inches = plots_per_line * 7.5
            height_inches = plot_lines * 5
             
            f, (axes) = plt.subplots(plot_lines, plots_per_line)
            axes=self._flatten_list(axes)
            f.set_size_inches(width_inches, height_inches)
            if self._deadline_list is None:
                deadline_list = [None]*len(self._file_names)
            else:
                deadline_list = self._deadline_list
            """ Subplotting."""
            for (ax, file_name, mon_data,
                 deadline) in zip(axes, self._file_names, monitor_data,
                                  deadline_list):
                ax_percent = ax.twinx()
                y_data = mon_data["throughputs"]
                if self._y_factor:
                    y_data = [float(y)*self._y_factor for y in y_data]                
                ax.plot(mon_data["time_stamps"],y_data)
                ax.set_title(file_name)
                ax.grid(alpha=0.5)
                ax.set_xlabel('time')
                ax.set_ylabel(self._y_label)
                if self._y_lim:
                    ax.set_ylim(self._y_lim)
                
                ax_percent.plot(mon_data["time_stamps"],
                                mon_data["file_percents"],
                                linestyle="-",
                                color="red")
                ax_percent.set_ylabel('% completed"')
                ax_percent.set_ylim((0.0, 100.0))
                
                if (self._deadline):
                    ax.axvline(self._deadline)
                    extra= (self._deadline-self._start_time)*0.10
                    ax.set_xlim((self._start_time, self._deadline+extra))
                
                if (deadline):
                    ax.axvline(deadline)
                    if x_lim:
                        ax.set_xlim(x_lim)
                    else:
                        extra= (deadline-self._start_time)*0.10
                        ax.set_xlim((self._start_time, deadline+extra))
            
            
            display.display(plt.show())
            display.clear_output(wait=True)
            time.sleep(self._refresh_rate)
            
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

