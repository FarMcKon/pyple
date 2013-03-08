#!/usr/bin/env python
from __future__ import ( unicode_literals, print_function, with_statement, absolute_import )
try:
    import unittest2
except ImportError, e:
    import unittest
import mock

import pypeople


class TestConfig(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_valid_conifg(self):
        """ test is_valid_config_json function """
        # HACK: always is true! Suckers!
        print("WARNING:is_valid_conifg_json is always TRUE")
        ret = pypeople.config.is_valid_config_json('fake text, should fail')
        self.assertTrue(ret)
        ret = pypeople.config.is_valid_config_json(None)
        self.assertTrue(ret)

    def test_has_config_file(self):
        ret = pypeople.config.has_config_file(None)
        # None case will return true if the machine has a config file at ~/.pypeople, we can't assume 
        # anything about dev's machines though we can't verify the return 
        print("for this uses machine, has config at ~/.pypeople is %s" %str(ret))
        ret = pypeople.config.has_config_file('tests/pypeople.test.config')
        self.assertTrue(ret)
        ret = pypeople.config.has_config_file('tests/no_such.config')
        self.assertFalse(ret)

    def retFalse(*args, **kwargs):
        return False

    @mock.patch.object(pypeople.config,'has_config_file',retFalse)
    def testGenerateConfig(self):
        """ tests that get_config will generate a config dict if 'has_config_file' is False"""
        configDict = pypeople.config.get_config()
        self.assertTrue('vcard_dir' in configDict)
        self.assertTrue('cfg_file' in configDict)
        self.assertTrue('cfg_file_version' in configDict)


class TestCards(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_dict_from_vcard(self):
        # non vcard makes an empty dict
        vcard = None
        dict = pypeople.cards.dict_from_vcard(vcard) 
        self.assertEqual( dict, {})
        
        # load a pre-known test vcard
    
    def test_get_vcard(self):
        example_filename = 'tests/Example1.vcf'
        try:
            vcard = pypeople.cards.get_vcard(example_filename)
        except IOError, e:
            self.assertFalse(True, "file load error %s" %e)
        keys = ['version', 'fn','n']
        for k in keys:
            self.assertTrue(k in vcard.contents.keys())


class TestHelpCommand(unittest.TestCase):
    """ Test the help command. Also a template for basic testing"""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testHelpIsCallable(self):
        self.assertTrue('help' in pypeople.utils.commandDict.keys())
        self.assertEqual( pypeople.utils.commandDict['help'], pypeople.utils.help )
        self.assertTrue( pypeople.utils.help.__doc__ is not None ) 
    
    def testHelpHasReturnString(self):
        helpOpts = ()
        x = pypeople.utils.commandDict['help']( 'help', helpOpts ) 
        self.assertIsNotNone(x)



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
                       'city': 'St. Paul','state':'MN', 'rest':'1020 Fumar St'},
                       {'src':'1034 Box 20, Chicago IA',
                       'city':'Chicago', 'state':'IA', 'rest':'1034 Box 20' },
                       ]
    addrCases = [{'src':"1020 Cedar Ave, Phila PA 13450",
			'city':'Phila','state':'PA','cc':'US','street':'1020 Cedar Ave'},
                 {'src':"1034 Box 20, Chicago IA, 12350",
			'city':'Chicago','state':'IA','street':'1020 Cedar Ave','cc':'US'},
		]

    def setUp(self):
        return

    def tearDown(self):
        return 

    def testCC(self):
        print('testing country code removal')
        for case in self.ccCases:
    	    test,cc,rest = case['src'], case['cc'],case['rest']

            ret_rest, ret_cc = pypeople.parsers.shitty_cc_parse(test)
            self.assertEquals(ret_rest, rest )
            self.assertEquals(ret_cc, cc)

    def testZip(self):
        print('testing Zip removal')
        for case in self.zipCases:
            test, zip, rest = case['src'], case['zip'],case['rest']

            ret_rest, ret_zip = pypeople.parsers.shitty_zip_parse(test)
            self.assertEquals(ret_rest, rest )
            self.assertEquals(ret_zip, zip)

    def testCityState(self):
        print('testing citystate match/removal')
        for case in self.cityStateCases:
            test, city, state, rest = case['src'], case['city'],case['state'],case['rest']

            ret_rest, ret_city, ret_state = pypeople.parsers.shitty_citystate_parse(test)
            self.assertEquals(ret_rest, rest)
            self.assertEquals(ret_city, city)
            self.assertEquals(ret_state, state)

    def test_shitty_addr_parser(self):
        for case in self.addrCases:
            result = pypeople.parsers.shitty_addr_parser(case['src'])
            self.assertEqual(result['cc'],case['cc'])
            self.assertEqual(result['city'],case['city'])


##  ============ Old test code. Remove as we port/create new code

#class TestBasics(unittest.TestCase):
#   
#    def test_get_all_vcard_elements(self):
#        vCard = utils.get_all_vcard_elements('tests/JoHacker.vcf')
#        self.assertIsNotNone(vCard)
#        self.assertEquals(len(vCard), 1)
#        contents = vCard[0].contents
#        self.assertItemsEqual(contents.keys(),('version','fn','n'))
#
#        vCard = utils.get_all_vcard_elements('tests/MultiJoHacker.vcf')
#        self.assertIsNotNone(vCard)
#        self.assertEquals(len(vCard), 2)
#        contents = vCard[1].contents
#        self.assertItemsEqual(contents.keys(),('version','fn','n'))
#    
#    def test_dict_from_vcard(self):
#        #This fails, TODO: fix
#        vCardList = utils.get_all_vcard_elements('tests/JoHacker.vcf')
#        vCard = vCardList[0]
#        ret = utils.dict_from_vcard(vCard)
#        self.assertItemsEqual(ret.keys(),('fullname','name','version'))
#
#        with self.assertRaises(Exception) as raises: #vobject.ParseError 
#            vCard = utils.get_all_vcard_elements('tests/BadJoHacker.vcf')
#            ret = utils.dict_from_vcard(vCard)
#        
#        # this fails on compex data
#        #vCardList = utils.get_all_vcard_elements('tests/MultiInfo.vcf')
#        #vCard = vCardList[0]
#        #ret = utils.dict_from_vcard(vCard)
#
#class VcardListTestCase(unittest.TestCase):
#
#    def setUp(self):
#	if config._g_config is None:
#	    config._g_config = {}
#        config._g_config['vcard_dir'] = './tests'
#
#    def tearDown(self):
#	config._g_config = None 
#
#    def testBasicList(self):
#	# hardcoded name list
#	ret = utils.vcard_list('list')
#	expected = u'MultiJoHacker,\tBadJoHacker,\tJoHacker,\tMultiInfo'
#	self.assertEqual(ret,expected)
#
#class VcardInitTestCase(unittest.TestCase):
#    FAKE_VCARD_DIR = './fake_vcard_dir'
#
#    def setUp(self):
#	#print('foo')
#	pass	
#
#    def tearDown(self):
#	#print('bar')
#	pass
#
#    def testBasicInitCase(self):
#	import os, stat, shutil
#	def remove_readonly(fn, path,excinfo):
#	    if fn is os.rmdir:
#		os.chmod(path, stat.S_IWRITE)
#		os.rmdir(path)
#	    elif fn is os.remove:
#		os.chmod(path, stat.S_IWRITE)
#		os.remove(path)
#
#	ret = utils.vcard_dir_init( 'init',self.FAKE_VCARD_DIR)
#	# verify our utils directory exists/works/etc and then remove it 
#	self.assertIsNone(ret)
#	self.assertTrue(os.path.isdir(self.FAKE_VCARD_DIR) )
#	#nuke the test dir
#	shutil.rmtree(self.FAKE_VCARD_DIR, onerror=remove_readonly)
#
#
#    
#    def testBasicInitFromRepoCase(self):
#	#self.assertTrue(False,"test case not written")
#	#ret = utils.vcard_dir_init( 'init','./tmp')
#	pass
#	


if __name__ == '__main__':
    unittest.main()
