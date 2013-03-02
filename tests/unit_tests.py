from __future__ import ( unicode_literals, print_function, with_statement, absolute_import )
import unittest
import pypeople

class TestBasicTestCase(unittest.TestCase):

    def testList():
        import pdb
        pdb.set_trace()
        pypeople.vcard_list('list','')

if __name__ == '__main__':
    unittest.main()
