#!/usr/bin/env python
from __future__ import (
    unicode_literals, print_function, with_statement, absolute_import)
import vobject
import subprocess

""" File containing Card reading/writing functions. """


def dict_from_vcard(vcard):
    """ loads a dictionary with *select* vcard info. NOTE: this does not
    load *all* vcard data, since that can be a bit batshit complex. It only
    loads some key values. Keep the origional vcard around to merge values back
    into it, or you *will lose data* esp for complex or edge-case data"""
    retDict = {}
    if vcard is None:
        return retDict  # return empty retDict
    # some VCARD keys are damm crpytic. Rekey them
    rekeyings = (('fullname', 'fn'), ('name', 'n'), ('address', 'adr'))
    contents = vcard.contents
    for key in contents.keys():
        #get our sub vCardObj, throwing errors as needed
        if len(contents[key]) == 0:  # hard to test,
            raise Exception("emtpy vcard key %s" % key)
        if len(contents[key]) > 1:
            debug.error("WARNING: More than one entry for vcard key %s" % key)
        vCardObj = contents[key][0]

        #unpack data out of the vcard objects
        unpackedData = None
        #raw string value, thank god
        if isinstance(vCardObj.value, type('str')):
            unpackedData = vCardObj.value
        elif isinstance(vCardObj.value, vobject.vcard.Name):
            unpackedData = {}
            unpackedData['given'] = vCardObj.value.given
            unpackedData['family'] = vCardObj.value.family
            unpackedData['additional'] = vCardObj.value.additional
            unpackedData['prefix'] = vCardObj.value.prefix
            unpackedData['suffix'] = vCardObj.value.suffix
        elif isinstance(vCardObj.value, vobject.vcard.Address):
            unpackedData = {}
            a = vCardObj.value
            unpackedData['street'] = a.street
            unpackedData['city'] = a.city
            unpackedData['region'] = a.region
            unpackedData['code'] = a.code
            unpackedData['country'] = a.country
        elif isinstance(vCardObj.value, list):
            unpackedData = vCardObj.value
        else:
            logging.debug("ohhhh! new datatype. We need to investigate!")
        #panic if we have no data
        if unpackedData is None:
            raise Exception("We do not know how to unpack key %s" % key)

        #outKey is our output key, it may be remapped
        outKey = key
        newkeys, oldkeys = zip(*rekeyings)
        if key in oldkeys:
            idx = oldkeys.index(key)
            outKey = newkeys[idx]
        retDict[outKey] = unpackedData

   #TODO: contine to extend this for addr, nickname
    # and other values
    print("TODO: extend this to other key values")
    return retDict


def vcard_merge_in_dict(inDict, vCard):
    """ merges a well-specified dictionary of data into the passed v-card"""
    #Since vcard can be complex, we expect you are updating an existing vcard
    #with dict values,  or maybe you created a fresh blank one to  pass us"
    #Assumes a well defined dict passed in
    # fullname: single string, full name. fullname generated from other name
    #strings if this is not defined
    # name : a dict, may contain 'given , middle, family' as keys or more
    rfinal_fn = 'fail'
    final_given = None
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
            vAddrObj = vobject.vcard.Address(
                addr_dict['street'], addr_dict['city'],
                addr_dict['region'], addr_dict['code'], addr_dict['country'])
            vCard.adr.value = vAddrObj

    if 'email' in inDict.keys():
        if 'email' not in contents.keys():
            vCard.add('email')
        vCard.email.value = inDict['email']
    if 'org' in inDict.keys():
        if 'org' not in contents.keys():
            vCard.add('org')
        vCard.org.value = inDict['org']  # org is a list?  not well doc'd


def get_vcard(vcard_fn):
    """ takes a caononical filename, returns a vcard object
    @param vcard_fn vcard filename
    @returns vcard for that filename, or None on error"""
    vCard = None
    with open(vcard_fn, 'rb') as fh:
        rawdata = fh.read()
        #TODO: handle error or fail cases better
        vCard = vobject.readOne(rawdata)
        #to read many entries per vcard, use 'get_all_vcard_elements' below
    return vCard


def cd_vcard_dir():
    """ Change our cwd to the vcard dir,
    @state-change: current working directory is changed
    @returns cur working directory before this was called,
        returns as string to be restored later.
    """
    cwd = os.getcwd()
    cfg = get_config()
    os.chdir(cfg['vcard_dir'])
    return cwd


def vcard_dir_sync(cmd, *args):
    """ sync our vcard file to our remote repo (if one exists) """
    #if len(args) == 0:    print( vcard_dir_sync.__doc__) #no options for sync, just run it
    if len(args) >= 1:
        print("attempt to sync param %s not understood" % args)

    cfg = get_config()
    if 'remote' in cfg.keys() and config['remote'] is not None:
        local_base = 'unknown'
        if 'vcard_dir' in cfg:
            local_base = cfg['vcard_dir']
        print("*****\n\tlocal dir:%s\n\tto remote:%s" % (
            os.path.expanduser(local_base), cfg['remote']))
        oldcwd = cd_vcard_dir()
        # PULL!
        cmd = ['git', 'pull']
        subprocess.call(cmd)

        #add all vcf files
        files = glob.glob(cfg['vcard_dir'] + '/*.vcf')
        cmd = ['git', 'add']
        cmd.extend(files)
        subprocess.call(cmd)

        ##make with the push
        import datetime
        dtString = str(datetime.datetime.now())
        cmd = ['git', 'commit', '--message="pypeople v%s autocommit on %s"' %
               (__version__, dtString)]
        #os.system(cmd)
        subprocess.call(cmd)
        cmd = 'git', 'push', 'origin', 'master'
        subprocess.call(cmd)
        #os.system(cmd)
        os.chdir(oldcwd)
        #FUTURE: we could use a lot better error tracking, etc here
        return True


def mkdir_p(path):
    """ a quick and dirty mkdir -p in python"""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise exc
