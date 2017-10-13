"""
This package provides a tool to monitor the size of a file in time. 
"""

import csv
import itertools
import os
import threading
import time

class FileMonitor:
    """
    FileMonitor reads the size of a file periodically and write a measure
    stamp on a destination (output) file including: timestamp, file size
    (bytes), % of completion, and size change throughput (bytes/s).
    
    The class provides a read_monitor_file to read an output file.
    """
    
    def __init__(self):
        self._keep_running=False
    
    def stop(self):
        """ Stops file monitoring. """
        self._keep_running=False
    
    
    def monitor_file_name_async(self, file_route, expected_size,
                                monitor_output_file,
                      format_string="{}:{}:{}:{}", sample_time_ms=1000,
                      use_modif_stamp=False,
                      max_timeout_ms=1000,
                      th_monitor_steps=100):
        """
        Starts monitoring of a file as a thread to not block code execution.
        
        Args:
          file_route: string route to file to be monitored.
          expected_size: expected size of the file in bytes as an integer.
          monitor_output_file: string  route to file where the monitoring
            samples will be written.
        format_string: format string used to write the simaples in the output
          file. It uses the str.format convention for four values in the
          following order: time_stamp, file_size, file_completion(%),
          throughput.
        sample_time_ms: time period in ms to monitor file.
        use_modif_stamps: if True, the timestamps recorded correspond to the
          last modification of file. If False, timestamps correspond to
          monitoring time.
        max_timeout_ms: Timeout in ms until subtrhead start is considered
          failed.
        th_monitor_steps: wait in ms to check if the subthread has started.
        
        Returns: True if the monitoring subthread starts successfuly.
        
        """
        self.th = threading.Thread(target=self.monitor_file_name,
                                       args=[file_route,
                                        expected_size,
                                        monitor_output_file],
                                        kwargs=dict(
                                        format_string=format_string,
                                        sample_time_ms=sample_time_ms,
                                        use_modif_stamp=use_modif_stamp))
        self.th.start()
        while not self._keep_running:
            max_timeout_ms-=th_monitor_steps
            if max_timeout_ms<0.0:
                return False
            time.sleep(float(th_monitor_steps)/1000)
        return True
    
    def monitor_file_name(self, file_route, expected_size, monitor_output_file,
                      format_string="{}:{}:{}:{}:", sample_time_ms=1000,
                      use_modif_stamp=False):
        """
        Starts monitoring of a file. This function never returns until stop()
        is called on the object.
        
        Args:
          file_route: string route to file to be monitored.
          expected_size: expected size of the file in bytes as an integer.
          monitor_output_file: string  route to file where the monitoring
            samples will be written.
        format_string: format string used to write the simaples in the output
          file. It uses the str.format convention for four values in the
          following order: time_stamp, file_size, file_completion(%),
          throughput.
        sample_time_ms: time period in ms to monitor file.
        use_modif_stamps: if True, the timestamps recorded correspond to the
          last modification of file. If False, timestamps correspond to
          monitoring time.
        """

        self._keep_running = True
        last_modif_stamp=None
        last_time_stamp=None
        last_file_size=None
        
        with open(monitor_output_file, "w"):
            pass
            
        
        while self._keep_running:
            time_stamp=time.time()
            (file_size, modif_stamp) = self.get_file_size(file_route)
            if modif_stamp is None:
                modif_stamp=time_stamp
            if use_modif_stamp:
                if last_modif_stamp==modif_stamp:
                    continue
                time_stamp = modif_stamp
                last_modif_stamp = modif_stamp
            percentage = 100.0*float(file_size)/float(expected_size)
            throughput=0
            
            if (last_time_stamp is None or last_file_size is None):
                throughput=float(file_size)
                last_time_stamp = time_stamp
                last_file_size = file_size
                continue
            else:
                bytes_written = file_size-last_file_size
                time_step = time_stamp - last_time_stamp
                throughput=float(bytes_written)/float(time_step)
                if throughput<0:
                    throughput=0.0
            
            last_time_stamp = time_stamp
            last_file_size = file_size
            
            self.write_sample(monitor_output_file, time_stamp, file_size,
                              percentage, throughput, format_string)
            time.sleep(float(sample_time_ms/1000))

    def get_file_size(self, file_route):
        """Returns the size in byts of a file pointed by file_route"""
        
        if not os.path.exists(file_route):
            return (0, None)
        statinfo = os.stat(file_route)
        return (statinfo.st_size, statinfo.st_mtime)
    
    def write_sample(self, output_file, time_stamp, size, percentage,
                     throughput, format_string):
        """Appends a measuring sample in and output file.
        
        Args:
          output_file: file system location to write the measuring sample in.
          timte_stamp: time object representing timestamp of the sample
          size: integer bytes representing size of the monitored file.
          percentage: float percentage of completion of the file.
          throughput: float observed growth in bytes/s.
          format_string: string instructing how those five values will be
            transformed in a string. Uses str.format convention.
        """
        with open(output_file, 'a+') as f:
            f.write(format_string.format(time_stamp, size, percentage,
                                         throughput,
                                         format_string)+"\n")
            
    @classmethod
    def read_monitor_file(cls, file_route,  separator=":"):
        """ Reads monitoring samples from a file and returns them as a dictionary
        of lists. It assumes that the file is a text file and each line is:
        "time_stamp (float epoch)s:file_size (int bytes)"
        ":file_percents(float percent):throughputs(float bytes/s"

        Args:
          file_route: string pointing to the samples file.
          separator: characters separating the values in each row.
        
        Returns: a dictionary of lists indexed by: time_stamps, file_sizes,
          file_percents, throughputs.
        """ 
        time_stamps = []
        file_sizes= []
        file_percents = []
        throughputs = []
        with open(file_route, "r") as f:
            reader1, reader2 = itertools.tee(csv.reader(f,
                                                        delimiter=separator))
            for row in reader2:
                if (len(next(reader1)) != 4):
                    continue
                time_stamps.append(float(row[0].strip()))
                file_sizes.append(int(row[1].strip()))
                file_percents.append(float(row[2].strip()))
                throughputs.append(float(row[3].strip()))
        return dict(time_stamps=time_stamps, file_sizes=file_sizes,
                    file_percents=file_percents, throughputs=throughputs ) 
        
    
            
            
            
