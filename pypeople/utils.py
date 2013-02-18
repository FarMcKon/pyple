#!/usr/bin/env python
from __future__ import ( unicode_literals, print_function, with_statement, absolute_import )

import subprocess
import glob
import optparse
import sys
import os
import json
import vobject
import re
import errno

#version, in the 3 main version formats
__version_info__ = [0,6,2,4]
__version__ = '0.6.2,4'
VERSION = '0.6.2,4'
# ^ For reasons specified elsewhere, this is done. Please don't get smart, it breaks
# some dependencies and it breaks setup.py
if __version__ != VERSION and VERSION != '.'.join([str(x) for x in __version_info__]):
    raise Exception("Version is screwed up")
#
#__version__ = '.'.join([str(x) for x in __version_info__])
#VERSION = __version__ 

_g_config = None # for singleton, always load via *get_config*

def is_valid_config_json(rawData):
    return True

#@memoize
def has_config_file(configFilename=None):
    """ quick check for config file existing. """
    file = configFilename if configFilename else '~/.pypeople'
    return os.path.isfile(os.path.expanduser(file))


def dict_from_vcard(vcard):
    """ loads a dictionary with *select* vcard info. NOTE: this does not
    load *all* vcard data, since that can be a bit batshit complex. It only
    loads some key values. Keep the origional vcard around to merge values back 
    into it, or you *will lose data* esp for complex or edge-case data"""
    retDict = {}
    # some VCARD keys are damm crpytic. Rekey them
    rekeyings= (('fullname','fn'),('name','n'),('address','adr'))
    contents = vcard.contents
    for key in contents.keys():
        #get our sub vCardObj, throwing errors as needed

        if len(contents[key]) == 0: #hard to test, 
            raise Exception("emtpy vcard key %s" %key)
        if len(contents[key]) > 1:
            import pdb
            pdb.set_trace()
            print("WARNING: More than one entry for vcard key %s" %key)
        vCardObj = contents[key][0]

        #unpack data out of the vcard objects
        unpackedData = None
        #raw string value, thank god
        if type(vCardObj.value) == type('str'):
            unpackedData = vCardObj.value 
        elif type(vCardObj.value) == vobject.vcard.Name:
            unpackedData = {}
            unpackedData['given'] = vCardObj.value.given
            unpackedData['family'] = vCardObj.value.family 
            unpackedData['additional'] = vCardObj.value.additional 
            unpackedData['prefix'] = vCardObj.value.prefix 
            unpackedData['suffix'] = vCardObj.value.suffix 
        elif type(vCardObj.value) is vobject.vcard.Address:
            unpackedData = {}
            a = vCardObj.value 
            unpackedData['street'] = a.street
            unpackedData['city'] = a.city
            unpackedData['region'] = a.region
            unpackedData['code'] = a.code
            unpackedData['country'] = a.country
        elif type(vCardObj.value) is list :
            unpackedData = vCardObj.value
        else:
            print("ohhhh! new datatype. We need to investigate!")
            import pdb
            pdb.set_trace()
        #panic if we have no data
        if unpackedData == None:
            import pdb
            pdb.set_trace()
            raise Exception("We do not know how to unpack key %s" %key)

        #outKey is our output key, it may be remapped
        outKey = key
        newkeys,oldkeys = zip(*rekeyings)
        if key in oldkeys:
            idx = oldkeys.index(key) 
            outKey = newkeys[idx]
        retDict[outKey] = unpackedData 

   #TODO: contine to extend this for addr, nickname
    # and other values 
    print("TODO: extend this to other key values")
    return retDict 

def shitty_cc_parse(addrLine):
    """Parses out countrycode from addressline
    @returns tuple of (reminingAddr, countrycode)"""
    shitty_cc = '(?P<cc>[a-zA-Z]{2,5})'
    shitty_break = "\s*?[.,]?\s*$"
    se = re.compile(shitty_cc + '$')
    cc = 'US'
    if se:
        grp = se.search(addrLine)
        if grp:
            cc = grp.groupdict()['cc']
            rest = addrLine[:grp.start()]
            # clear off  the comma, and break chars
            grp2 = re.search(shitty_break,rest)
            if grp2:
                rest = rest[:grp2.start()]
            return (rest, cc)
    return (addrLine, cc)

def shitty_zip_parse(addrLine):
    """Parse out countrycode from addressline
    @returns tuple of (reminingAddr, countrycode)"""
    shitty_zip = '(?P<zip>\d{5})'
    shitty_break = "\s*?[.,]?\s*$"
    se = re.compile(shitty_zip + '$')
    zip = ''
    if se:
        grp = se.search(addrLine)
        if grp:
            zip = grp.groupdict()['zip']
            rest = addrLine[:grp.start()]
            # clear off the comma, and break chars
            grp2 = re.search(shitty_break,rest)
            if grp2:
                rest = rest[:grp2.start()]
            return (rest, zip)
    return (addrLine, zip)

def shitty_citystate_parse(addrLine):
    """ parse out city/state data from addr
    @return tuple of (rest, city, state) """
    shitty_state='(?P<state>\w[.,]?\w[.,]?)'
    shitty_city='(?P<city>\w+[.-]?\s*?\w*?)' # 
    shitty_break='\s*?[.,]?\s*$'
    se = re.compile( shitty_city + '\s+' + shitty_state + '$') 
    state = ''
    if se:
        grp = se.search(addrLine)
        if grp:
            state = grp.groupdict()['state']
            city = grp.groupdict()['city']
            rest = addrLine[:grp.start()] 
            # clear off the comma, and break chars
            grp2 = re.search(shitty_break,rest)
            if grp2:
                rest = rest[:grp2.start()]
            return (rest, city, state)
    return (addrLine,'', '')


def shitty_addr_parser(addrLine):
    """shitty address parser. Assumes US always"""
    shitty_state = '(P<st>\w[.,]?{2}|\w{3,6})'
    shitty_break = '\s*,?\s+'
    shitty_city = '(P<city>\w+)' #won't handle St. Foobra, or other cities
                            #with breaks. Shitty, no? 
    final_zip = None
    shitty_zip = '(?P<zip>\d{5})'
    #FUTURE: pull countrycode off the end
    #ma = re.compile(shitty_cc + '$') 
    addrLeft = addrLine
    ma = re.compile(shitty_zip + '$')
    grp = ma.search(addrLeft)
    if grp:
        final_zip = grp.groupdict['cc']
        addrLeft = addrLeft[:grp.span()[1]] 
    else:
        final_zip = ''
        #addrLeft unmutilated

    ma = re.compile(shitty_state)

    #shitty_addr_regex = "\s+,?\s+(?P<name>[1-9]{5})"
    #re.search("(?P<city>\w{2}|\w{3,6})\s+(?P<name>[1-9]{5})",ad).groupdict()



def shitty_addr_parser(addrLine):
    """shitty address parser. Assumes US always"""
    shitty_state = '(?P<st>\s([a-zA-Z][.,]?){2}(\s|,))'
    shitty_break = '\s*,?\s+'
    shitty_city = '(?P<city>\w+)' #won't handle St. Foobra, or other cities
                            #with breaks. Shitty, no? 
    shitty_zip = '(?P<zip>\d{5})'
    #FUTURE: pull countrycode off the end
    #ma = re.compile(shitty_cc + '$') 
    addrLeft = addrLine
    ma = re.compile(shitty_zip + '$')
    grp = ma.search(addrLeft)
    if grp:
        final_zip = grp.groupdict()['zip']
        addrLeft = addrLeft[:grp.span()[0]] 
    else:
        final_zip = ''
        #addrLeft unmutilated

    grp = None
    ma = re.compile(shitty_state)
    grp = ma.search(addrLeft)
    if grp:
        final_state = grp.groupdict()['st']
        addrLeft = addrLeft[:grp.span()[0]] 
        import pdb
        pdb.set_trace()
    else:
        final_state = ''

    shitty_addr_regex = "\s+,?\s+(?P<name>[1-9]{5})"
    #re.search("(?P<city>\w{2}|\w{3,6})\s+(?P<name>[1-9]{5})",ad).groupdict()


def vcard_merge_in_dict(inDict, vCard):
    """ merges a well-specified dictionary of data into the passed v-card"""
    #Since vcard can be complex, we expect you are updating an existing vcard
    #with dict values,  or maybe you created a fresh blank one to  pass us"
    #Assumes a well defined dict passed in
    # fullname: single string, full name. fullname generated from other name 
    #strings if this is not defined
    # name : a dict, may contain 'given , middle, family' as keys or more
    rfinal_fn = 'fail'
    final_given= None
    final_family = None
    final_other = 'fail_firstname'
    final_nick = 'fail_nick'
    
    if 'nick' in inDict.keys():
        final_nick = inDict['nick']

    if 'fullname' in inDict.keys():
        final_fn = inDict['fullname']
    if 'name' in inDict.keys():
        final_family = inDict['name']['family']
        final_given = inDict['name']['given']
    elif 'nick' in inDict.keys():
        final_fn = 'nick'
    else:
        #import pdb
        #pdb.set_trace()
        raise Exception("No Name Match, assuming Not Specified")
        # TODO: smater fallback generation
    #TODO: only add keys if it's not found
    contents = vCard.contents
    if 'fn' not in contents.keys():
        vCard.add('fn')
    vCard.fn.value = final_fn
    if 'n' not in contents.keys():
        vCard.add('n')
    #TODO: SMARTER NAME OBJECT GENERATION
    vNameObj = vobject.vcard.Name(final_nick)
    if final_given is not None and final_family is not None:
        vNameObj = vobject.vcard.Name(family=final_family, given=final_given)
        vCard.n.value = vNameObj 
    
    if 'address' in inDict.keys():
        addr_dict = inDict['address']
        if addr_dict != {}:
            if 'adr' not in contents.keys():
                vCard.add('adr')
            vAddrObj = vobject.vcard.Address(addr_dict['street'],addr_dict['city'],
                addr_dict['region'],addr_dict['code'], addr_dict['country'])
            vCard.adr.value= vAddrObj

    if 'email' in inDict.keys():
        if 'email' not in contents.keys():
            vCard.add('email')
        vCard.email.value = inDict['email']
    if 'org' in inDict.keys():
        if 'org' not in contents.keys():
            vCard.add('org')
        vCard.org.value = inDict['org'] #org is a list?  not well doc'd

def get_config() :
    """ load config, assuming it exists. If no config, sets
    some basic values into the global config object """
    global _g_config
    if _g_config != None:
        return _g_config #already loaded, reuse singleton

    cfg_file = '~/.pypeople'
    if not has_config_file(cfg_file):
        _g_config = {}
        _g_config['vcard_dir'] = os.getcwd()
        _g_config['cfg_file'] = None
        _g_config['cfg_version'] = __version_info__
        return _g_config
    cfg_full = os.path.expanduser(cfg_file)
    with open(cfg_full, 'rb') as fh:
        rawdata = fh.read()
        data = json.loads(rawdata)
        if is_valid_config_json(data):
            _g_config = data
            return _g_config 
    print("unspecified load config error")
    return None 

def __help(cmd, *args):
    """Print a help menu for the user"""
    print('help (aka %s) called with %s' %(cmd, args) ) 
    print('pypeople: Command line tool for vcard management, with git backend')
    print('Version: ' + __version__ )
    print("Available Commands:")
    for cmd in availSubCmds.keys():
        helptxt = availSubCmds[cmd].__doc__ if availSubCmds[cmd].__doc__ else 'Undocumented'
        print('\t'+str(cmd) +':\t ' + helptxt)

def vcard_find(cmd, *args):
    """Find a nickname based on a name/string/something as part of the vcard"""
    if len(args) == 0:
        print(vcard_find.__doc__)
        return
    if len(args) > 0:
        import pdb
        pdb.set_trace()
        regStr = ' '.join(args)
        config = get_config()
        # no options, just print all 
        matches = []
        files = glob.glob(config['vcard_dir']+'/*.vcf')
        for f in files:
            with open(f, "r") as fh:
                data = fh.read() 
                match = re.search(re.escape(regStr), data,re.IGNORECASE)
                if match != None:
                    nick = f[len(config['vcard_dir'])+1:-4] #strip dir portions
                    print(nick)
                    matches.append(nick)
            
        print( ',\t'.join(matches) )
                    
def vcard_dir_init(cmd, *args):
    """Create/Update a config file. 'init <dir_of_vfc> [remote repo]' """
    print('init (aka %s) called with %s' %(cmd, args) )
    dir, remote = None, None
    if len(args) == 0:
        print(vcard_dir_init.__doc__)
        print('initalize in dir, pulling from remote_repo as needed ')
        return False
    if len(args) > 0:  
        dir = args[0]
    if len(args) > 1:
        remote = args[1]
    if len(args) > 2:
        print ("too many params for init!")
        return False
    config = get_config()
    import os
    config['vcard_dir'] = os.path.abspath(os.path.expanduser(dir))
    config['cfg_file'] = os.path.abspath(os.path.expanduser('~/.pypeople'))
    config['cfg_version'] = __version_info__
    config['remote'] = None

    if remote != None:
        config['remote'] = remote
        
    with open(config['cfg_file'],'w+') as fh:
        raw = json.dumps(config, indent=2)
        fh.write(raw)
        print('written')

    if not os.path.isdir(config['vcard_dir']):
       mkdir_p(config['vcard_dir'])
       print('making new dir for contacts at %s' %config['vcard_dir'])
       if 'remote' in config.keys():
            if not os.path.isdir(config['remote']):
               #no dir exists, do a simple git clone 
                print("settings vcard dir %s to track git remote %s" 
                      %(config['vcard_dir'], config['remote']))
                cmd2 = ['git','clone',config['remote'], config['vcard_dir'] ]
                subprocess.call(cmd2)#FUTURE: make less of a giant os security hole
                #os.system(cmd2) #FUTURE: make less of a giant os security hole
            else:
                print("cannot git init an existing dir yet. Sorry :( ")
                print("directory %s already exists" %config['remote'])
                return False
                #FUTURE: be smart, and init over the existing dir anyway
                #cmd = 'git init ' + config['vcard_dir']
                #subprocess.call(cmd2)#FUTURE: make less of a giant os security hole
                #os.system(cmd) #FUTURE: make less of a giant os security hole

def cd_vcard_dir():
    """ changes our cwd to the vcard dir, 
    @returns cwd from entry, to be restored later """
    cwd = os.getcwd()
    config = get_config()
    os.chdir(config['vcard_dir'])
    return cwd


def vcard_dir_sync(cmd, *args):
    """ sync our vcard file to our remote repo (if one exists) """

    if len(args) == 0:    print( vcard_dir_sync.__doc__)
    if len(args) >= 1:    
        print("sync param %s not understood" %args)

    config = get_config()
    if 'remote' in config.keys() and config['remote'] != None:
        oldcwd = cd_vcard_dir()
        cmd = ['git','pull' ]
        #os.system(cmd)
        #add all vcf files
        files = glob.glob(config['vcard_dir']+'/*.vcf')
        cmd = ['git','add']
        cmd.extend(files)
        subprocess.call(cmd)
        #os.system(cmd)
        #make with the push
        import datetime
        dtString = str(datetime.datetime.now())
        cmd = ['git','commit','--message="pypeople v%s autocommit on %s"' %(__version__, dtString)]
        #os.system(cmd)
        subprocess.call(cmd)
        cmd = 'git','push','origin','master'
        subprocess.call(cmd)
        #os.system(cmd)
        os.chdir(oldcwd)
        #FUTURE: we could use a lot better error tracking, etc here
        return True
    
  

def mkdir_p(path):
    """ a quick and dirty mkdir -p in python"""
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: 
            raise exc 


def vcard_list(cmd, *args):
    """list : Lists all vCards in vcard folder, take a regex someday"""
    config = get_config()
    # no options, just print all 
    files = glob.glob(config['vcard_dir']+'/*.vcf')
    #strip directory and file ending
    nicks = [fname[len(config['vcard_dir'])+1:-4] for fname in files]
    strRet = u''
    if len(args) == 0 : 
       strRet +  ',\t'.join(nicks) 
    elif len(args) > 0:
        if args[0] == '--help':
            strRet + vcard_list.__doc__
        else:
            regStr = ' '.join(args)
            # try case sensitive first
            caseMatch = False
            regObj = re.compile(re.escape(regStr))
            for nick in nicks:
                if regObj.search(nick):
                    strRet + nick
                    caseMatch = True
            # no case match, search case insensitive
            if not caseMatch:
                regObj = re.compile(re.escape(regStr), re.IGNORECASE)
                for nick in nicks:
                    if regObj.search(nick):
                        strRet + nick
    return strRet

def whois(cmd, *args):
    """whois <nick> display info on a single exact nick """
    nick = None
    if len(args) == 0:
        print(whois.__doc__)
        return False
    if len(args) > 0:  
        nick = args[0]
    if len(args) > 1:  
       print("too many params, try single-quote around names")
       raise Exception("too many params, try single-quote around names")

    #load config, 
    config = get_config()

    nick_fn = nick + '.vcf'
    nick_fn = os.path.join(config['vcard_dir'],nick_fn)
    
    if not os.path.isfile(nick_fn):
            print("ERROR: old nickname %s does not exist at %s" 
                  %(nick, nick_fn) )
            return True
    allVcards = get_all_vcard_elements(nick_fn)
    if len(allVcards) == 0:
        raise Exception("No vcards in nick file !" %nick_fn)
    if len(allVcards) > 1:
        raise Exception("Multiple Vcards in one file. We are too stupid to hadle this!")
    vCard = allVcards[0]
    #vCard = getvcard(nick_fn)

    infoDict = dict_from_vcard(vCard)
    for k in infoDict.keys():
        if type(infoDict[k]) is dict:
            print(k + '::' )
            for subk in infoDict[k]:
                print( '\t'+ subk + ':' + str(infoDict[k][subk]) )
        else: 
            print(k + u':' + str(infoDict[k]) )

def vcard_rm(cmd, *args):
    """rm <nick> delete a vcard file """
    oldnick = None
    if len(args) == 0:
        print( rm.__doc__ )
        return False
    if len(args) > 0:  
        oldnick = args[0]
    if len(args) > 1:  
       print("too many params")
       raise Exception("too many params")

    #load config, 
    config = get_config()

    oldnick_fn = oldnick + '.vcf'
    oldnick_fn = os.path.join(config['vcard_dir'],oldnick_fn)
    
    if not os.path.isfile(oldnick_fn):
            print("ERROR: old nickname %s does not exist at %s" 
                  %(oldnick, oldnick_fn) )
            return True

    # I choose os.system menthod, since it's easy to read/parse,
    # other os mv might be easier or more portable. Might be a security hole
    cmd = ['rm', oldnick_fn]
    os.system(' '.join(cmd) )
    return True

def getvcard(vcard_fn):
    """ takes a caononical filename, returns a vcard object
    @returns vcard for that filename, or None on error"""
    get_config()
    vCard = None
    with open(vcard_fn,'rb') as fh:
        rawdata = fh.read()
        #TODO: handle error or fail cases better
        vCard = vobject.readOne(rawdata)
        #to read many entries per vcard, use 'get_all_vcard_elements' below
    return vCard 

def get_all_vcard_elements(vcard_fn):
    """Loads and returns  a list of all vcard elements in the specified file.
    @returns a list of all VCARD entries in the specified file. Empty list of no vcard in file
    """
    vCardList = []
    with open(vcard_fn,'rb') as fh:
        rawdata = fh.read()
        #TODO: handle error or fail cases better
        for obj in vobject.readComponents(rawdata):
            if obj.name == 'VCARD':
               vCardList.append(obj)
    return vCardList 



def vcard_mv(cmd, *args):
    """mv <oldnick> <newnick>: move a vcard to a new nickname """
    oldnick = newnick = None
    if len(args) == 0:
        print( mv.__doc__)
        return False
    if len(args) > 0:  
        oldnick = args[0]
    if len(args) > 1:  
        newnick = args[1]
    if len(args) > 2:  
       print("too many params")
       raise Exception("too many params")

    #load config, 
    config = get_config()

    newnick_fn = newnick + '.vcf'
    oldnick_fn = oldnick + '.vcf'
    oldnick_fn = os.path.join(config['vcard_dir'],oldnick_fn)
    newnick_fn = os.path.join(config['vcard_dir'],newnick_fn)
   
    #TODO: Refactor to load old vcard, update nickname (if in vcard)
    # save new vcard, then delete old vcard once new vcard is saved
    if not os.path.isfile(oldnick_fn):
            print("ERROR: old nickname %s does not exist at %s" 
                  %(oldnick, oldnick_fn) )

    if os.path.isfile(newnick_fn):
        print("ERROR: new nickname %s exists for a previous vcard at %s" 
              %(newnick, newnick_fn) )
        raise Exception("colliding nicknames")

    # I choose os.system menthod, since it's easy to read/parse,
    # other os mv might be easier or more portable
    cmd = ['mv', oldnick_fn, newnick_fn]
    os.system(' '.join(cmd) )
    print("oldnick at %s moved to newnick at %s" %(oldnick_fn, newnick_fn))


def undefined(cmd, *args):
    """Lazy programmer has not written this function"""
    print('undefined %s called with %s' %(cmd, args) )

#def example(cmd. args):
    #example
    #config = get_config()
    #if len(args) == 0:    print( add_addr.__doc__)
    #if len(args) >= 1:    nick = paramLine[0]
    ## other param breakdown here 
    #vcard_fn = nick + '.vcf'
    #vcard_fn = os.path.join(config['vcard_dir'] ,vcard_fn)
    #vCard = getvcard(vcard_fn)
    #infoDict = dict_from_vcard(vCard)
    ## make changes to infodict here
    #newVCard = vcard_from_dict(infoDict)
    #rawdata = newVCard.serialize()
    #with open(vcard_fn,'w+') as fh:
    #    fh.write(rawdata)

def add_org(cmd, *args):
    """org <nick> <org> add org to an existing vcard"""

    config = get_config()
    nick , org = None, None
    if len(args) == 0:    print( add_org.__doc__)
    if len(args) >= 1:    
        nick = args[0]
    if len(args) >= 2:
        org = args[1]
    if len(args) >= 3:
        print("only <nick> <org_addr> understood :(")
    # other param breakdown here 
    vcard_fn = nick + '.vcf'
    vcard_fn = os.path.join(config['vcard_dir'] ,vcard_fn)
    vCard = getvcard(vcard_fn)
    infoDict = dict_from_vcard(vCard)
   

    infoDict['org'] = [org,] #list-ize. Dunnow why yet

    ## make changes to infodict here
    vcard_merge_in_dict(infoDict,vCard)
    rawdata = vCard.serialize()
    with open(vcard_fn,'w+') as fh:
        fh.write(rawdata)
    return True

def add_phone(cmd, *args):
    """phone <nick> <number>:  add phone number string to an existing vcard"""

    config = get_config()
    nick , email = None, None
    if len(args) == 0:    print( add_email.__doc__)
    if len(args) >= 1:    
        nick = args[0]
    if len(args) >= 2:
        phone = args[1:]
    if len(args) >= 3:
        print("phone number ot understood ")

    # other param breakdown here 
    vcard_fn = nick + '.vcf'
    vcard_fn = os.path.join(config['vcard_dir'] ,vcard_fn)
    vCard = getvcard(vcard_fn)
    #infoDict = dict_from_vcard(vCard)
    infoDict  = {}
    infoDict['phone'] = email
    

    ## make changes to infodict here
    vcard_merge_in_dict( infoDict,vCard)
    rawdata = vCard.serialize()
    with open(vcard_fn,'w+') as fh:
        fh.write(rawdata)
 
def add_email(cmd, *args):
    """email <nick> <email> add email to an existing vcard"""

    config = get_config()
    nick , email = None, None
    if len(args) == 0:    print( add_email.__doc__)
    if len(args) >= 1:    
        nick = args[0]
    if len(args) >= 2:
        email = args[1]
    if len(args) >= 3:
        print("only <nick> <email_addr> understood :(")
    # other param breakdown here 
    vcard_fn = nick + '.vcf'
    vcard_fn = os.path.join(config['vcard_dir'] ,vcard_fn)
    vCard = getvcard(vcard_fn)
    infoDict = dict_from_vcard(vCard)
    
    infoDict['email'] = email
    

    ## make changes to infodict here
    vcard_merge_in_dict(infoDict,vCard)
    rawdata = vCard.serialize()
    with open(vcard_fn,'w+') as fh:
        fh.write(rawdata)
 
def add_addr(cmd, *args):
    """addr <nick> <addr_chunk> : add meatspace address to contact"""
    config = get_config()
    nick = None
    if len(args) == 0:
        print( add_addr.__doc__)
    if len(args) >= 1:
        nick = args[0]
    if len(args) >= 2:
        addr_list= args[1:]
    vcard_fn = nick + '.vcf'
    vcard_fn = os.path.join(config['vcard_dir'] ,vcard_fn)
    #print('expecting file at %s' %vcard_fn)

    vCard = getvcard(vcard_fn)
    infoDict = dict_from_vcard(vCard)
    addr = ' '.join(addr_list)

    # break addr down into chunks using our shitty regex sys
    # zip and country code can be None, the rest must exist
    rest, country = shitty_cc_parse(addr)
    rest2, zip = shitty_zip_parse(rest)
    rest3, city, state = shitty_citystate_parse(rest2)
    street = rest3
    addrDict = {'street':street,'city':city,'region':state,
                'code':zip, 'country':country}
    if 'address' in infoDict.keys():
        print("has address: %s replacing" %str(infoDict['address']))
    infoDict['address'] = addrDict
   
    # geneate our new vcard
    newVCard = vobject.vCard()
    vcard_merge_in_dict(infoDict,newVCard)
    rawdata = newVCard.serialize()
    with open(vcard_fn,'w+') as fh:
        fh.write(rawdata)
 
    return True 

def add_contact(cmd, *args):
    """add <nick> ["full name"] [email], [phone]"""
    config = get_config() 
    nick = None
    if len(args) == 0:
        print( add_contact.__doc__)
    if len(args) >= 1:
        nick = args[0]
        fulname = nick #fullname fallback
    if len(args) >= 2:
        fullname = args[1]
        #print('fullname %s' %fullname)
    else:
        print("cant handle those params " + str(args))
    
    vcard_fn = nick + '.vcf'
    vcard_fn = os.path.join(config['vcard_dir'] ,vcard_fn)
    #print('expecting file at %s' %vcard_fn)

    info = {}
    info['nick'] = nick
    info['fullname'] = fullname
    if len(fullname.split(' ')) > 1:
        subname = fullname.split()
        info['name'] = {'family':subname[0], 'given':subname[1]}
    if os.path.isfile(vcard_fn):
        print('file exists for %s, at %s please move or rename it' 
                %(nick, vcard_fn) )
        return False
    vcard = vobject.vCard()
    if os.path.isfile(vcard_fn):
        vcard = loadcraphere
    else:
        vcard_merge_in_dict(info, vcard)
    rawdata = vcard.serialize()
    with open(vcard_fn,'w+') as fh:
        fh.write(rawdata)
        #print('written, sucker!')
    #annoyingly verbose vcard here'
    #Full Name = fn. Single string, entire name, required
    #x = vobject.vCard()
    # x.name = 'Foo'


if __name__ == '__main__':
    #print('main')
    caller = None
    subCmd = 'help'
    cmdRest = []
    if len(sys.argv) > 0:
        caller = sys.argv[0]
    if len(sys.argv) > 1:
        subCmd = sys.argv[1]
    if len(sys.argv) > 2:
        cmdRest = sys.argv[2:]

    availSubCmds = {
        'list': vcard_list,
        'init': vcard_dir_init,
        'add': add_contact,
        'addr': add_addr,
        'rm':  vcard_rm,
        'mv': vcard_mv,
        'name': undefined,
        'whois': whois,
        'rename': undefined,
        'email': add_email,
        'phone': add_phone,
        'bday': undefined,
        'org': add_org,
        'help':  __help,
        'sync':vcard_dir_sync,
        'find':vcard_find,
    }
    

    if subCmd in availSubCmds.keys():
        if (availSubCmds[subCmd] != None):
            func = availSubCmds[subCmd]
            # run the function with unkonwn params. 
            result = func(subCmd, *cmdRest) 
            print( result )
    else:
        print("command '%s' not found. try 'help' to list commands" %subCmd)
