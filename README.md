# PyPeople: Command Line AddressBook in Python

PyPeople is a python command-line address book, with optional git-syncing.

Inspired by ppl (ruby commandline addressbook) and with some vacation time to spare, I've put together pypeople. 


# Overview
PyPeople makes it easy to create or edit vcf files. If you don't have a ~/.pypeople file (created by the 'init' command), it will list/edit/create vCard .vcf files in the directroy pypeople is running in.

If you do run 'init' you can create a config file (stored at ~/.pypeople) to specify a vCard contact directory, and an optional git repository to sync contacts to/from.


# See Also 
#vobject 0.8.1c
#dulwich
