"""Module to coordinate monitoring and plotting for multiple files."""

import ntpath
import signal
import sys
import time

from filemon import FileMonitor
import filemon.graph as gr
import filemon.rest_reporter as rr


class IntCapturer(object):
    
    
    def program_capture_stop(self, objects_to_stop):
        self._objects_to_stop=objects_to_stop
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.pause()
    
    def signal_handler(self, signal, frame):
        for obj in self._objects_to_stop:
            obj.stop_threads()
        print ("Exit of threads completed")
        
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
    rest_reporting: if True the measurements will be posted to a REST service
      on http://hostname:port/api/file/[file_id]
    """
    file_monitors = [] 
    monitor_objects=[]
    for (file_route, i, expected_size) in zip(file_routes,
                                              range(len(file_routes)),
                                              expected_sizes):
        file_monitor = "monitor.{}.{}".format(i,ntpath.basename(file_route))
        fm = FileMonitor()
        fm.monitor_file_name_async(file_route, expected_size,
                                        file_monitor)
        monitor_objects.append(fm)
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
    cap=IntCapturer()
    cap.program_capture_stop([thread]+monitor_objects)
    
    
class RestOrchestrator(object):
    """ This class reads from a REST call what files should be monitored and
    configures filemonitors, plot, and reporting funcitons automatically.
    The class keeps checking the REST configuraiton end point and if changes
    appear, they are re-applied.
    """
    
    def set_initial_settings(self, measurement_id_list, title_list, y_lim=None,
                             y_label="bytes/s", y_factor=None,
                             rest_reporting=False,
                             hostname="127.0.0.1", port=5000):
        self._id_list=measurement_id_list
        self._y_lim=y_lim
        self._data_dic={}
        self._rest_reporting=rest_reporting
        self._hostname=hostname
        self._port=port
        
        for (m_id, title, i) in (self._id_list, title_list,
                                 range(len(self._id_list))):
            self._data_dc[m_id] = dict(active=False,
                                       file_route=None,
                                       deadline=time.time()+100,
                                       file_monitor=None,
                                       title=title,
                                       index=i)
        self._monitor_count=0
        self.create_initial_monitors()
        self.create_graph_manager(rest_reporting, y_label, y_factor, y_lim,
                                  title_list)
        self.program_capture_stop()
        
    def program_capture_stop(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.pause()
    def get_field(self, field):
        return [self._data_dic[x][field] for x in self._id_list] 
    def get_file_monitor_files(self):
        return [x.monitor_output_file for x in self.get_field("file_monitor")]
    
    def signal_handler(self, signal, frame):
        self._graph_manager.stop_threads()
        for obj in self.get_field("file_monitor"):
            obj.stop_threads()
        print ("Exit of threads completed")
          
    
    def create_monitor(self, file_route, expected_size):
        self._monitor_count+=1
        file_monitor = "monitor.{}.{}".format(self._monitor_count,
                                              ntpath.basename(file_route))
        fm = FileMonitor()
        fm.monitor_file_name_async(file_route, expected_size,
                                        file_monitor)
        return fm

    def create_initial_monitors(self):
        for (m_id, m_data) in self._data_dic.items():
            mon = self.create_monitor("/tmp/fake.{}",format(m_id),
                                      1)
            m_data["file_monitor"]=mon
    
    def create_graph_manager(self, rest_reporting, y_label, y_factor, y_lim,
                            title_list):
        monitor_files=self.get_file_monitor_files()
        if not rest_reporting:
            thread  = gr.DataPlot(title_list,
                                 monitor_files,
                                  y_label=y_label, 
                                  y_factor=y_factor, y_lim=y_lim)
        else:
            
            file_id_dict={x:y for (x,y) in zip(monitor_files, self._id_list)}
            thread  = rr.RestReporter(title_list, monitor_files, y_label=y_label, 
                              y_factor=y_factor, y_lim=y_lim)
            thread.set_rest_server_ip(self._hostname, self._port)
            thread.set_files_rest_ids(file_id_dict)
            
        thread.set_deadline_list(self.get_field("deadline"))
        thread.daemon = True
        self._graph_manager=thread
        thread.start()
    
    
    def reconfigure(self, measurement_id, file_route=None, 
                    expected_size=None, deadline=None):
        """(re)configures a measurement"""
        if file_route is not None or expected_size is not None:
            new_monitor=self.create_monitor(file_route, expected_size)
            old_monitor=self._data_dic[measurement_id]["file_monitor"]
            self._data_dic[measurement_id]["file_monitor"]=new_monitor
            self._graph_manager._file_monitors=self.get_file_monitor_files()
            old_monitor.stop_threads()
        
        if deadline is not None:
            self._graph_manager._deadline_list=self.get_field("deadline")
            
        
            
            
        
        
        
        
