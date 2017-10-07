import os
from test import TestFileGeneric
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
    