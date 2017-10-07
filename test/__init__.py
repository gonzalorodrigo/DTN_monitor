

import os
import shutil
from unittest import TestCase



class TestFileGeneric(TestCase):
    def _register_tmp_file(self, tmp_file):
        self.addCleanup(os.remove, tmp_file)
        self.assertFalse(os.path.isfile(tmp_file), "Temporary file {} exists"
                         " before starting!".format(tmp_file))
        
    def _register_tmp_folder(self, tmp_file):
        self.addCleanup(shutil.rmtree, tmp_file)
        self.assertFalse(os.path.isfile(tmp_file), "Temporary file {} exists"
                         " before starting!".format(tmp_file))
        self.assertFalse(os.path.exists(tmp_file), "Temporary folder {} exists"
                         " before starting!".format(tmp_file))
        
 
    def _create_empty(self, file_name, is_folder=False):
        if not is_folder:
            with open(file_name, 'a'):
                os.utime(file_name, None)
        else:
            os.makedirs(file_name)