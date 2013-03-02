from __future__ import ( unicode_literals, print_function, with_statement, absolute_import )
import unittest
import pypeople
import os

class TestBasicTestCase(unittest.TestCase):
    def setUp(self):
        # override pypeople._g_config singlton to point to test config
        g_config = {}
        g_config['vcard_dir'] = os.getcwd() + '/tests'
        g_config['cfg_version'] = pypeople.__version_info__
        g_config['cfg_file'] = None
        self.old_cfg = pypeople._g_config
        pypeople._g_config = g_config
               
        


    def testList(self):
        retStr = pypeople.vcard_list('list')
        print(retStr)
        # spot check some known example people
        if ' , ' in retStr  and 'JoHacker' in retStr:
            self.assertTrue(True)
        else:
            self.assertFalse(True)
        retStr = pypeople.vcard_list('list','Hacker')
        print(retStr)
        # spot check some known example people
        if ' , ' in retStr  and 'JoHacker' in retStr:
            self.assertTrue(True)
        else:
            self.assertFalse(True)
 

if __name__ == '__main__':
    unittest.main()
