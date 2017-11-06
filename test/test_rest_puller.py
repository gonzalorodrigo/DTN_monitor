import time
import unittest

import requests_mock

from filemon.orchestrate import RestPuller


class TestRestPuller(unittest.TestCase):
    def setUp(self):
        self.rp=None
    def tearDown(self):
        if self.rp is not None:
            self.rp.stop_threads()
        
    def changes_receiver(self, received_obj):
        self._received_content.append(received_obj)
        
    def test_pull(self):
        self._received_content=[]
        with requests_mock.mock() as m:
            m.get('http://test.com:1234/api/', json={"ID":"val"})
            self.rp = RestPuller("test.com", 1234, "api/",
                           self.changes_receiver)
            self.rp.start()
            
            time.sleep(1)
            self.assertGreaterEqual(len(self._received_content), 1)
            self.assertEqual(self._received_content, 
                           [{"ID":"val"}] )
            
    
    
    