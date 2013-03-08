#!/usr/bin/env python
from __future__ import (
    unicode_literals, print_function, with_statement, absolute_import)
import re


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
            grp2 = re.search(shitty_break, rest)
            if grp2:
                rest = rest[:grp2.start()]
            return (rest, cc)
    return (addrLine, cc)


def shitty_zip_parse(addrLine):
    """Parse out countrycode from addressline
    @param address line
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
            grp2 = re.search(shitty_break, rest)
            if grp2:
                rest = rest[:grp2.start()]
            return (rest, zip)
    return (addrLine, zip)


def shitty_citystate_parse(addrLine):
    """ parse out city/state data from addr
    @return tuple of (rest, city, state) """
    shitty_state = '(?P<state>\w[.,]?\w[.,]?)'
    shitty_city = '(?P<city>\w+[.-]?\s*?\w*?)'
    shitty_break = '\s*?[.,]?\s*$'
    se = re.compile(shitty_city + '\s+' + shitty_state + '$')
    state = ''
    if se:
        grp = se.search(addrLine)
        if grp:
            state = grp.groupdict()['state']
            city = grp.groupdict()['city']
            rest = addrLine[:grp.start()]
            # clear off the comma, and break chars
            grp2 = re.search(shitty_break, rest)
            if grp2:
                rest = rest[:grp2.start()]
            return (rest, city, state)
    return (addrLine, '', '')


def shitty_addr_parser(addrLine):
    """shitty address parser. Assumes US .
    @param addrLine: address string, assumed to be a us address
    @returns a dict of {'state','street','city','zip', 'rest'}
     state, street, city, zip are componets of a US address,
        'rest' is inparsable data as a string
    """
    retDict = {}
    addrLeft, cc = shitty_cc_parse(addrLine)
    retDict['cc'] = 'US' if cc is None else cc

    addrLeft, retDict['zip'] = shitty_zip_parse(addrLeft)
    addrLeft, retDict['city'], retDict[
        'state'] = shitty_citystate_parse(addrLeft)
    retDict['street'] = addrLeft
    return retDict
##    shitty_state = '(?P<st>\s([a-zA-Z][.,]?){2}(\s|,))'
##    shitty_break = '\s*,?\s+'
##    shitty_city = '(?P<city>\w+)' #won't handle St. Foobra, or other cities
##                            #with breaks. Shitty, no?
##    shitty_zip = '(?P<zip>\d{5})'
##    retDict = {}
##    #FUTURE: pull countrycode off the end
##    #ma = re.compile(shitty_cc + '$')
##    addrLeft = addrLine
##    ma = re.compile(shitty_zip + '$')
##    grp = ma.search(addrLeft)
##    if grp:
##        final_zip = grp.groupdict()['zip']
##        addrLeft = addrLeft[:grp.span()[0]]
##    else:
##        final_zip = ''
##        #addrLeft unmutilated
##    retDict['zip'] = final_zip
##
##    grp = None
##    ma = re.compile(shitty_state)
##    grp = ma.search(addrLeft)
##    if grp:
##        final_state = grp.groupdict()['st']
##        addrLeft = addrLeft[:grp.span()[0]]
##    else:
##        final_state = ''
##    retDict['state'] = final_state
##
##    grp = None
##    shitty_addr_regex = "(?P<street>.*?)(?=\s?,)"
##    ma = re.compile(shitty_addr_regex)
##    grp = ma.search(addrLeft)
##    if grp:
##      final_street= grp.groupdict()['street']
##      addrLeft = addrLeft[grp.span()[1]:]
##    else:
##      final_street = ''
##    retDict['street'] = final_street
##
##    grp = None
##    shitty_addr_regex = ",\s*(?P<city>\S+)(\s|\w)"
##    ma = re.compile(shitty_addr_regex)
##    grp = ma.search(addrLeft)
##    if grp:
##      final_city= grp.groupdict()['city']
##      addrLeft = addrLeft[:grp.span()[0]]
##    else:
##      final_city= ''
##    retDict['city'] = final_city
##
##    retDict['rest'] = addrLeft
##    return retDict
##  #re.search("(?P<city>\w{2}|\w{3,6})\s+(?P<name>[1-9]{5})",ad).groupdict()
##
#
