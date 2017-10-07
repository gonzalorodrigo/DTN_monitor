import os
import threading
import time


class FileMonitor:
    
    def stop(self):
        self._keep_running=False
    
    def monitor_file_name(self, file_route, expected_size, monitor_output_file,
                      format_string="{}:{}:{}", sample_time_ms=1000,
                      use_modif_stamp=False, async_call=False, max_timeout=1.0):
        if async_call:
            self.th = threading.Thread(target=self.monitor_file_name,
                                       file_route=file_route,
                                        expected_size=expected_size,
                                        monitor_output_file=monitor_output_file,
                                        format_string=format_string,
                                        sample_time_ms=sample_time_ms,
                                        use_modif_stamp=use_modif_stamp,
                                        async_call=False)
            self.th.start()
            monitor_step=0.1
            while not self._keep_running:
                max_timeout-=monitor_step
                if max_timeout<0.0:
                    return False
                time.sleep(monitor_step)
            return True
            
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
        
    
            
            
            
