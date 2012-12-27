# pyple: Command Line AddressBook in Python

Pyple (prononunced 'pie-ple') is a python command-line address book, with optional git-syncing.

Inspired by ppl (ruby commandline addressbook) and with some vacation time to spare, I've put together pyple. 


# Overview
pyple makes it easy to create or edit vcf files. If you don't have a ~/.pyple file (created by the 'init' command), it will list/edit/create vCard .vcf files in the directroy pyple is running in.

If you do run 'init' you can create a config file (stored at ~/.pyple) to specify a vCard contact directory, and an optional git repository to sync contacts to/from.


# See Also 
vobject 0.8.1c
dulwich
ppl: http://news.ycombinator.com/item?id=4947047
