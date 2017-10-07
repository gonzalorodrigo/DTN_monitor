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
        
    def test_get_file_size(self):
        
        monitored_file = os.path.join(self.tmp_folder, "file.txt")
        self._register_tmp_file(monitored_file)
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
        self._register_tmp_file(monitored_file)
        
        fm = FileMonitor()
        time_stamp = 5000
        fm.write_sample(monitored_file,time_stamp, 10, 5.0,"{}:{}:{}")
        fm.write_sample(monitored_file,time_stamp+2, 12, 6.0,"{}:{}:{}")
        
        with open(monitored_file, 'r') as f:
            lines = f.readlines()
            
            self.assertEqual(lines,
                             ["5000:10:5.0"
                              "5002:12:6.0" ])
            
            
              

    