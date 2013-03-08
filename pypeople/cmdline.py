#!/usr/bin/env python
from __future__ import (
    unicode_literals, print_function, with_statement, absolute_import)
""" Command line tools for/from pypeople """

import sys
import utils


def main(*args, **kwargs):
    """ main function for command line pypeople tool. """
    calledVia = None
    command = 'help'
    cmdOpts = []
    if len(sys.argv) > 0:
        calledVia = sys.argv[0]
    if len(sys.argv) > 1:
        command = sys.argv[1]
    if len(sys.argv) > 2:
        cmdOpts = sys.argv[2:]
    returnString = utils.try_command(command, cmdOpts)
    print(returnString)
