#!/usr/bin/env python
from __future__ import ( unicode_literals, print_function, with_statement, absolute_import )

from pypeople import utils 
import unittest

class TestBasics(unittest.TestCase):
   
    def test_is_valid_conifg(self):
        """ test is_valid_config_json function """
        # HACK: always is true! Suckers!
        print("is_valid_conifg_json is always TRUE")
        ret = utils.is_valid_config_json('fake text, should fail')
        self.assertTrue(ret)
        ret = utils.is_valid_config_json(None)
        self.assertTrue(ret)

    def test_has_config_file(self):
        ret = utils.has_config_file(None)
        #no assumptions, we don't know their dev machine
        ret = utils.has_config_file('tests/pypeople.test.config')
        self.assertTrue(ret)


    def test_get_all_vcard_elements(self):
        vCard = utils.get_all_vcard_elements('tests/JoHacker.vcf')
        self.assertIsNotNone(vCard)
        self.assertEquals(len(vCard), 1)
        contents = vCard[0].contents
        self.assertItemsEqual(contents.keys(),('version','fn','n'))

        vCard = utils.get_all_vcard_elements('tests/MultiJoHacker.vcf')
        self.assertIsNotNone(vCard)
        self.assertEquals(len(vCard), 2)
        contents = vCard[1].contents
        self.assertItemsEqual(contents.keys(),('version','fn','n'))
    
    def test_dict_from_vcard(self):
        #This fails, TODO: fix
        vCardList = utils.get_all_vcard_elements('tests/JoHacker.vcf')
        vCard = vCardList[0]
        ret = utils.dict_from_vcard(vCard)
        self.assertItemsEqual(ret.keys(),('fullname','name','version'))

        with self.assertRaises(Exception) as raises: #vobject.ParseError 
            vCard = utils.get_all_vcard_elements('tests/BadJoHacker.vcf')
            ret = utils.dict_from_vcard(vCard)
        
        # this fails on compex data
        #vCardList = utils.get_all_vcard_elements('tests/MultiInfo.vcf')
        #vCard = vCardList[0]
        #ret = utils.dict_from_vcard(vCard)


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
                       {'src':"1020 Fumar St, St. Paul MN",
                       'city': 'St. Paul','state':'MN',
                       'rest':'1020 Fumar St'},
                              ]
    addrCases = [ "1020 Cedar Ave, Phila PA 13450", 
                 "1034 Box 20 Chicago, IA, 12350", ]

    def setUp(self):
        #print("setup") 
        return

    def tearDown(self):
        #print('tearDown')
        return 

    def testCC(self):
        #print('testing country code removal')
        for case in self.ccCases:
            test,cc,rest = case['src'], case['cc'],case['rest']

            ret_rest, ret_cc = utils.shitty_cc_parse(test)
            self.assertEquals(ret_rest, rest )
            self.assertEquals(ret_cc, cc)

    def testZip(self):
        #print('testing Zip removal')
        for case in self.zipCases:
            test, zip, rest = case['src'], case['zip'],case['rest']

            ret_rest, ret_zip = utils.shitty_zip_parse(test)
            self.assertEquals(ret_rest, rest )
            self.assertEquals(ret_zip, zip)

    def testCityState(self):
        #print('testing citystate match/removal')
        for case in self.cityStateCases:
            test, city, state, rest = case['src'], case['city'],case['state'],case['rest']

            ret_rest, ret_city, ret_state = utils.shitty_citystate_parse(test)
            self.assertEquals(ret_rest, rest)
            self.assertEquals(ret_city, city)
            self.assertEquals(ret_state, state)

    def test_shitty_addr_parser(self):
        for case in self.addrCases:
            result = utils.shitty_addr_parser(case)
            import pdb 
            pdb.set_trace()
            print (result)


if __name__ == '__main__':
    unittest.main()
