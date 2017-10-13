"""
python -m unittest test.test_filemon

"""

import os
from test import TestFileGeneric
import time
from unittest import TestCase

from filemon import FileMonitor


class TestFileMonitor(TestFileGeneric):
    
    tmp_folder = "/tmp/dtnmontest/"
    def setUp(self):
        self._register_tmp_folder(self.tmp_folder)
        self._create_empty(self.tmp_folder, is_folder=True)
        self._fm=None
    
    def tearDown(self):
        if self._fm:
            self._fm.stop()
            time.sleep(1)
    def test_get_file_size(self):
        
        monitored_file = os.path.join(self.tmp_folder, "file.txt")
        self._create_empty(monitored_file)
        
        fm = FileMonitor()
        
        self.assertEqual(0, fm.get_file_size(monitored_file)[0])
        with open(monitored_file, 'a+') as f:
            f.write("a")
        self.assertEqual(1, fm.get_file_size(monitored_file)[0])
        with open(monitored_file, 'a+') as f:
            f.write("a")
        self.assertEqual(2, fm.get_file_size(monitored_file)[0])
        
    def test_write_sample(self):
        monitored_file = os.path.join(self.tmp_folder, "file.txt")
        
        fm = FileMonitor()
        time_stamp = 5000
        fm.write_sample(monitored_file,time_stamp, 10, 5.0, 20.0, 
                        "{}:{}:{}:{}")
        fm.write_sample(monitored_file,time_stamp+2, 12, 6.0, 21.0,
                        "{}:{}:{}:{}")
        
        with open(monitored_file, 'r') as f:
            lines = f.readlines()
            lines = [x.rstrip('\n') for x in lines]
            
            self.assertEqual(lines,
                             ["5000:10:5.0:20.0",
                              "5002:12:6.0:21.0" ])
    
    def test_monitor_file_name(self):
        monitored_file = os.path.join(self.tmp_folder, "file.txt")
        self._create_empty(monitored_file)
        output_file = os.path.join(self.tmp_folder, "output.txt")
        
        self._fm = FileMonitor()
        self._fm.monitor_file_name_async(monitored_file, 10, output_file,
                      format_string="{},{},{}", sample_time_ms=1000)
        
        
        time.sleep(0.5)
        ref_ts = time.time()
        with open(monitored_file, 'a') as f:
            f.write("a")
        time.sleep(1)
        with open(output_file, 'r') as f:
            lines = f.readlines()
            lines = [x.rstrip('\n') for x in lines]
            self.assertEqual([",".join(x.split(",")[1:]) for x in lines],
                             ["0,0.0",
                              "1,10.0"])
            self.assertTrue(float(lines[0].split(",")[0])-ref_ts < 2)
            self.assertTrue(float(lines[0].split(",")[0])-(ref_ts+1) 
                                   < 2)
        with open(monitored_file, 'a') as f:
            f.write("b")
        time.sleep(1)
    
        with open(output_file, 'r') as f:
            lines = f.readlines()
            lines = [x.rstrip('\n') for x in lines]
            self.assertEqual([",".join(x.split(",")[1:]) for x in lines],
                             ["0,0.0",
                              "1,10.0",
                              "2,20.0"])
            self.assertTrue(float(lines[0].split(",")[0])-ref_ts < 1)
            self.assertTrue(float(lines[1].split(",")[0])-(ref_ts+1) 
                                   < 1)
            self.assertTrue(float(lines[2].split(",")[0])-(ref_ts+3) 
                                   < 1)
            
    def test_read_monitor_file(self):
        output_file = os.path.join(self.tmp_folder, "output.txt")
        with open(output_file, 'w') as f:
            f.write("10.0:0:0.0:0.0\n")
            f.write("11.0:10:15.0:10.0\n")
            f.write("12.0:20:25.0:20.0\n")
        
        read_data=FileMonitor.read_monitor_file(output_file)
        self.assertEqual(read_data,
                         dict(time_stamps=[10.0,11.0,12.0],
                              file_sizes=[0,10,20],
                              file_percents=[0.0,15.0, 25.0],
                              throughputs=[0.0,10.0,20.0]))
        
        
    def test_read_monitoring_process(self):
        monitored_file = os.path.join(self.tmp_folder, "file.txt")
        self._create_empty(monitored_file)
        output_file = os.path.join(self.tmp_folder, "output.txt")
        
        self._fm = FileMonitor()
        self._fm.monitor_file_name_async(monitored_file, 10, output_file,
                      sample_time_ms=1000)
        
        
        time.sleep(0.5)
        ref_ts = time.time()
        with open(monitored_file, 'a') as f:
            f.write("a")
        time.sleep(1)

        with open(monitored_file, 'a') as f:
            f.write("b")
        time.sleep(1)
        self._fm.stop()
        
        read_data=FileMonitor.read_monitor_file(output_file)
        self.assertEqual(read_data["file_sizes"], [0,1,2])
        self.assertEqual(read_data["file_percents"], [0.0,10.0,20.0])
        for (a,b) in zip(read_data["throughputs"], [0.0, 1, 1]):
            self.assertAlmostEqual(a,b,places=2)
        self.assertTrue(read_data["time_stamps"][0]-ref_ts < 1)
        self.assertTrue(read_data["time_stamps"][1]-(ref_ts+1) 
                                   < 1)
        self.assertTrue(read_data["time_stamps"][2]-(ref_ts+3) 
                                   < 1)
        
        
        

            
            
              

    