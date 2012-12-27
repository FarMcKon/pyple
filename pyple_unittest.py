#!/usr/bin/env python
from __future__ import ( unicode_literals, print_function, with_statement, absolute_import )

import pypl
import unittest

class TestAddrParseBasicTestCase(unittest.TestCase):
    """ Basic US address Test Cases"""
    ccCases = [{'src':'1024 Cedar Ave, Phila PA 19143, US',
                'cc': 'US','rest':'1024 Cedar Ave, Phila PA 19143'},
               {'src':'Box 2103 Phila PA, 19143, USA',
                'cc': 'USA','rest':'Box 2103 Phila PA, 19143'},
               {'src':'1024 Cedar Ave, Phila PA 19143',
                'cc': 'US','rest':'1024 Cedar Ave, Phila PA 19143'},
                      ]
    zipCases = [{'src':'1024 Cedar Ave, Phila PA 19143',
                'zip': '19143','rest':'1024 Cedar Ave, Phila PA'},
               {'src':'Box 2103 Phila PA, 19143',
                'zip': '19143','rest':'Box 2103 Phila PA'},
               {'src':'1024 Cedar Ave, Phila PA',
                'zip': '','rest':'1024 Cedar Ave, Phila PA'}, 
                      ]

    cityStateCases = [{'src':'1024 Cedar Ave, Phila PA',
                       'city': 'Phila','state':'PA',
                       'rest':'1024 Cedar Ave'},
                      {'src':'1020 Fumar St, St. Paul MN',
                       'city': 'St. Paul','state':'MN',
                       'rest':'1020 Fumar St'},
                              ]

    def setUp(self):
        print("setup") 
    def tearDown(self):
        print('tearDown')


    def testCC(self):
        print('testing country code removal')
        for case in self.ccCases:
            test,cc,rest = case['src'], case['cc'],case['rest']

            ret_rest, ret_cc = pypl.shitty_cc_parse(test)
            self.assertEquals(ret_rest, rest )
            self.assertEquals(ret_cc, cc)

    def testZip(self):
        print('testing Zip removal')
        for case in self.zipCases:
            test, zip, rest = case['src'], case['zip'],case['rest']

            ret_rest, ret_zip = pypl.shitty_zip_parse(test)
            self.assertEquals(ret_rest, rest )
            self.assertEquals(ret_zip, zip)

    def testCityState(self):
        print('testing citystate match/removal')
        for case in self.cityStateCases:
            test, city, state, rest = case['src'], case['city'],case['state'],case['rest']

            ret_rest, ret_city, ret_state = pypl.shitty_citystate_parse(test)
            self.assertEquals(ret_rest, rest)
            self.assertEquals(ret_city, city)
            self.assertEquals(ret_state, state)

if __name__ == '__main__':
    unittest.main()
