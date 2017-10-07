"""
python -m unittest test.test_filemon

"""

import os
import threading
import time


class FileMonitor:
    
    def stop(self):
        self._keep_running=False
    
    
    def monitor_file_name_async(self, file_route, expected_size,
                                monitor_output_file,
                      format_string="{}:{}:{}", sample_time_ms=1000,
                      use_modif_stamp=False,
                      max_timeout_ms=1000,
                      th_monitor_steps=100):
        
        self.th = threading.Thread(target=self.monitor_file_name,
                                       file_route=file_route,
                                        expected_size=expected_size,
                                        monitor_output_file=monitor_output_file,
                                        format_string=format_string,
                                        sample_time_ms=sample_time_ms,
                                        use_modif_stamp=use_modif_stamp)
        self.th.start()
        while not self._keep_running:
            max_timeout_ms-=th_monitor_steps
            if max_timeout_ms<0.0:
                return False
            time.sleep(float(th_monitor_steps)/1000)
        return True
    
    def monitor_file_name(self, file_route, expected_size, monitor_output_file,
                      format_string="{}:{}:{}", sample_time_ms=1000,
                      use_modif_stamp=False):

        self._keep_running = True
        last_modif_stamp=None
        while self._keep_running:
            time_stamp=time.time()
            (file_size, modif_stamp) = self.get_file_size(file_route)
            if use_modif_stamp:
                if last_modif_stamp==modif_stamp:
                    continue
                time_stamp = modif_stamp
                last_modif_stamp = modif_stamp
            percentage = 100.0*float(file_size)/float(expected_size)
            
            self.write_sample(monitor_output_file, time_stamp, file_size,
                              percentage, format_string)
            time.sleep(float(sample_time_ms/1000))

    def get_file_size(self, file_route):
        statinfo = os.stat(file_route)
        return (statinfo.st_size, statinfo.st_mtime)
    
    def write_sample(self, output_file, time_stamp, size, percentage,
                     format_string):
        with open(output_file, 'a+') as f:
            f.write(format_string.format(time_stamp, size, percentage,
                                         format_string))
        
    
            
            
            
