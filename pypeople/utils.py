#!/usr/bin/env python
from __future__ import ( unicode_literals, print_function, with_statement, absolute_import )
try:
    from . import config
except ValueError:
    import config 
import subprocess
import glob
#import optparse
#import sys
#import os
#import json
#import re
#import errno
#import sets
#
#version, in the 3 main version formats
__version_info__ = [0,6,2,4]
__version__ = '0.6.2,4'
VERSION = '0.6.2,4'
# ^ For reasons specified elsewhere, this is done. Please don't get smart, it breaks
# some dependencies and it breaks setup.py
if __version__ != VERSION and VERSION != '.'.join([str(x) for x in __version_info__]):
    raise Exception("Version is screwed up")

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(filename='log_filename.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('This is a log message.')

commandDict = {}# list of callable functions. Func in this takes (*args **kwards) and returns a string

class cmdlineCommand(object):
    """Decorator to add a function to our dict of command line commands"""

    def __init__(self, funcName):
        #TRICKY: decorator with arguments, the arguments (but not function) are passed here
        self.funcName = funcName

    def __call__(self, func):
        #TRICKY: decorator with arguments, function only is passed here
	    global commandDict
	    if self.funcName in commandDict:
	        raise Exception("Duplicate utility Function")
	    commandDict[self.funcName] = func
	    logging.debug("adding function %s to funcitonDict" %func.__name__)
	    return func
	

@cmdlineCommand('help')
def help(cmd,cmdArgs):
    """Get help on pypeople, a vCard management tool"""
    global commandDict
    retInfo = []
    if len(cmdArgs) > 0:
        #return help on a single function
        if cmdArgs[0] in commandDict.keys():
            return commandDict[cmdArgs[0]].__doc__

    #else, return general info
    retInfo = ['pypeople: A command line tool for vCard management',
            'Version:' + __version__,
            'Available Commands:']
    #fill in more info here
    for cmdName in  commandDict.keys():
        cmdFunc = commandDict[cmdName]
        cmdDoc = str(cmdName) + ': '+ str(cmdFunc.__doc__) if cmdFunc.__doc__ is not None else 'Undocumented Function'
        retInfo.append('\t'  +cmdDoc)

    return '\n'.join(retInfo)

@cmdlineCommand('list')
def vcard_list(cmd, *args):
    """Lists all vCards in the contacts folder, can take a regex """
    cfg = config.get_config()
    logging.debug("in vcard_list")
    # no options, just print all 
    files = glob.glob(cfg['vcard_dir']+'/*.vcf')
    #strip directory and file ending
    nicks = [fname[len(cfg['vcard_dir'])+1:-4] for fname in files]
    strRet = ''
    if len(args) == 0 : 
       strRet = ',\t'.join(nicks) 
       logging.debug("no args")
       return strRet
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


@cmdlineCommand('find')
def vcard_find(cmd, *args):
    """find a card by name/string/something search of vcards."""
    if len(args) == 0: 
        return vcard_find.__doc__
    if len(args) > 0:
        regStr = ' '.join(args)
        cfg = get_config()

        # no options, just print all 
        matches = sets.Set()
        files = glob.glob(cfg['vcard_dir']+'/*.vcf')
        for f in files:
            with open(f, "r") as fh:
                data = fh.read() 
                match = re.search(re.escape(regStr), data,re.IGNORECASE)
                if match != None:
                    nick = f[len(cfg['vcard_dir'])+1:-4] #strip dir portions
                    matches.add(nick)
        return  ',\t'.join(matches)

 
@cmdlineCommand('init')
def vcard_dir_init(cmd, *args):
    """Create/Update a config file. 'init <dir_of_vfc> [remote repo]' """
    #print('init (aka %s) called with %s' %(cmd, args) )
    dir, remote = None, None
    if len(args) == 0:
        print(vcard_dir_init.__doc__)
        print('initalize in dir, pulling from remote_repo as needed ')
        return False
    if len(args) > 0:  #target init dir
        dir = args[0]
    if len(args) > 1: # source repo if cloning
        remote = args[1]

    if len(args) > 2:
        print ("too many params for init!")
        return False
    cfg = get_config()
    cfg['vcard_dir'] = os.path.abspath(os.path.expanduser(dir))
    cfg['cfg_file'] = os.path.abspath(os.path.expanduser('~/.pypeople'))
    cfg['cfg_version'] = __version_info__
    cfg['remote'] = None

    if remote != None:
        cfg['remote'] = remote
        
    with open(cfg['cfg_file'],'w+') as fh:
        raw = json.dumps(cfg, indent=2)
        fh.write(raw)
        print('written')

    if not os.path.isdir(cfg['vcard_dir']):
        mkdir_p(cfg['vcard_dir'])
        print('making new dir for contacts at %s' %cfg['vcard_dir'])
        if 'remote' in cfg.keys():
            if cfg['remote'] == None:
                raise Exception('cfg remote is None')
            elif cfg['remote'] != None and not os.path.isdir(config['remote']):
                print("settings vcard dir %s to track git remote %s" 
                      %(cfg['vcard_dir'], config['remote']))
                cmd2 = ['git','clone',cfg['remote'], config['vcard_dir'] ]
                subprocess.call(cmd2)#FUTURE: make less of a giant os security hole
                #os.system(cmd2) #FUTURE: make less of a giant os security hole
                return 'clone attempted'
            else:
                print("cannot git init an existing dir yet. Sorry :( ")
                print("directory %s already exists" %config['remote'])
                return 'Failed, no remote specified'

                #FUTURE: be smart, and init over the existing dir anyway
                #cmd = 'git init ' + cfg['vcard_dir']
                #subprocess.call(cmd2)#FUTURE: make less of a giant os security hole
                #os.system(cmd) #FUTURE: make less of a giant os security hole

@cmdlineCommand('whois')
def whois(cmd, *args):
    """whois <nick> display info on a single exact nick """
    nick = None
    if len(args) == 0:
        return str(whois.__doc__)
    if len(args) > 0:  
        nick = args[0]
    if len(args) > 1:  
       print("too many params, try single-quote around names")
       raise Exception("too many params, try single-quote around names")

    #load config, 
    cfg = get_config()

    nick_fn = nick + '.vcf'
    nick_fn = os.path.join(cfg['vcard_dir'],nick_fn)
    
    if not os.path.isfile(nick_fn):
            return ("ERROR: old nickname %s does not exist at %s" 
                  %(nick, nick_fn) )
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

@cmdlineCommand('rm')
def vcard_rm(cmd, *args):
    """rm <nick> delete a vcard file """
    oldnick = None
    if len(args) == 0:
        return str( rm.__doc__ )
    if len(args) > 0:  
        oldnick = args[0]
    if len(args) > 1:  
       return "too many params"
       #raise Exception("too many params")

    #load config, 
    cfg = get_config()

    oldnick_fn = oldnick + '.vcf'
    oldnick_fn = os.path.join(cfg['vcard_dir'],oldnick_fn)
    
    if not os.path.isfile(oldnick_fn):
            return "ERROR: old nickname %s does not exist at %s"  %(oldnick, oldnick_fn) 

    # I choose os.system menthod, since it's easy to read/parse,
    # other os mv might be easier or more portable. Might be a security hole
    cmd = ['rm', oldnick_fn]
    os.system(' '.join(cmd) )
    return ''


#@cmdlineCommand('testCmdName')
##def example(cmd. args):
#    #example
#    #cfg = get_config()
#    #if len(args) == 0:    print( add_addr.__doc__)
#    #if len(args) >= 1:    nick = paramLine[0]
#    ## other param breakdown here 
#    #vcard_fn = nick + '.vcf'
#    #vcard_fn = os.path.join(cfg['vcard_dir'] ,vcard_fn)
#    #vCard = getvcard(vcard_fn)
#    #infoDict = dict_from_vcard(vCard)
#    ## make changes to infodict here
#    #newVCard = vcard_from_dict(infoDict)
#    #rawdata = newVCard.serialize()
#    #with open(vcard_fn,'w+') as fh:
#    #    fh.write(rawdata)


# template/placeholder for a function. used for testing
@cmdlineCommand('testCmdName')
def undefined(cmd, *args):
    """Lazy programmer has not written this function"""
    return 'undefined %s called with %s' %(cmd, args) 

@cmdlineCommand('org')
def add_org(cmd, *args):
    """org <nick> <org> add org to an existing vcard"""

    cfg = get_config()
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
    vcard_fn = os.path.join(cfg['vcard_dir'] ,vcard_fn)
    vCard = getvcard(vcard_fn)
    infoDict = dict_from_vcard(vCard)
    infoDict['org'] = [org,] #list-ize. Dunnow why yet

    ## make changes to infodict here
    vcard_merge_in_dict(infoDict,vCard)
    rawdata = vCard.serialize()
    with open(vcard_fn,'w+') as fh:
        fh.write(rawdata)
    return True


@cmdlineCommand('phone')
def add_phone(cmd, *args):
    """phone <nick> <number>:  add phone number to an existing vcard"""

    cfg = get_config()
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
    vcard_fn = os.path.join(cfg['vcard_dir'] ,vcard_fn)
    vCard = getvcard(vcard_fn)
    #infoDict = dict_from_vcard(vCard)
    infoDict  = {}
    infoDict['phone'] = email
    

    ## make changes to infodict here
    vcard_merge_in_dict( infoDict,vCard)
    rawdata = vCard.serialize()
    with open(vcard_fn,'w+') as fh:
        fh.write(rawdata)
 
@cmdlineCommand('email')
def add_email(cmd, *args):
    """email <nick> <email> add email to an existing vcard"""

    cfg = get_config()
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
    vcard_fn = os.path.join(cfg['vcard_dir'] ,vcard_fn)
    vCard = getvcard(vcard_fn)
    infoDict = dict_from_vcard(vCard)
    
    infoDict['email'] = email
    

    ## make changes to infodict here
    vcard_merge_in_dict(infoDict,vCard)
    rawdata = vCard.serialize()
    with open(vcard_fn,'w+') as fh:
        fh.write(rawdata)
 

@cmdlineCommand('addr')
def add_addr(cmd, *args):
    """addr <nick> <addr_chunk> : add meatspace address to contact"""
    cfg = get_config()
    nick = None
    if len(args) == 0:
        print( add_addr.__doc__)
    if len(args) >= 1:
        nick = args[0]
    if len(args) >= 2:
        addr_list= args[1:]
    vcard_fn = nick + '.vcf'
    vcard_fn = os.path.join(cfg['vcard_dir'] ,vcard_fn)
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

@cmdlineCommand('add')
def add_contact(cmd, *args):
    """add <nick> ["full name"] [email], [phone]"""
    cfg = get_config() 
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
    vcard_fn = os.path.join(cfg['vcard_dir'] ,vcard_fn)
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

@cmdlineCommand('mv')
def vcard_mv(cmd, *args):
    """mv <oldnick> <newnick>: move a vcard to a new nickname """
    oldnick = newnick = None
    if len(args) == 0:
        return mv.__doc__
        return False
    if len(args) > 0:  
        oldnick = args[0]
    if len(args) > 1:  
        newnick = args[1]
    if len(args) > 2:  
       return "too many params"

    #load config, 
    cfg = get_config()

    newnick_fn = newnick + '.vcf'
    oldnick_fn = oldnick + '.vcf'
    oldnick_fn = os.path.join(cfg['vcard_dir'],oldnick_fn)
    newnick_fn = os.path.join(cfg['vcard_dir'],newnick_fn)
   
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


def try_command(commandName, commandOptsList):
    """ Tries to run a vcard commnad from our command dict.
    @param commandName : string name of the command called
    @param commandOptList: list of command options
    @return: string of results to display to user
    """
    retString = help.__doc__ #default to help doc
    if commandName in commandDict.keys():
        retString = commandDict[commandName](commandName, commandOptsList)
    return retString
 

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
 


