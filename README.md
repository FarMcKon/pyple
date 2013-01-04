# PyPeople: Command Line AddressBook in Python

PyPeople is a python command-line address book, with optional git-syncing.

Inspired by ppl (ruby commandline addressbook) and with some vacation time to spare, I've put together pypeople. 


# Overview
PyPeople makes it easy to create or edit vcf files. If you don't have a ~/.pypeople file (created by the 'init' command), it will list/edit/create vCard .vcf files in the directroy pypeople is running in.

If you do run 'init' you can create a config file (stored at ~/.pypeople) to specify a vCard contact directory, and an optional git repository to sync contacts to/from.

## help
    pypeople help 
Displays help commands for the most common commands

## init 
    pypeople init ~/Contacts
    pypeople init ~/Contacts git@github.com/User/PrivateContacts
Creates a config file for pypeople at ~/.pypeople with the given optoins. The first option is your vcard contacts directory, the second is an optional git repository which sync will use to push/pull contact info from.

f you never run this command, pypeople will assume the directroy you are in is your contacts, and the 'sync' command will be disabled.
 
## add  
    pypeople add jrand "J Random Hack"
    pypeople add jrand "J Random Hack" jrand@eample.org 555-123-4567
Creates a vcard 'jrand.vcf' in your contacts directory containing the name (and email/phone if specified) entered. If you have never run init, pypeople will assume your contacts are in the directory it is running in.  If a card of that name exists, you will get an error

## addr
    pypeople addr jrand "5000 Some St, Broolyn NY 14554"
    pypeople addr jrand 5000 Some St, Broolyn NY 14554

Adds an address to the vcard for jrand.  We have simple US address parsing, other addresses may be (sorry) a bit mangled


## See Also 
This project uses vobject[http://pypi.python.org/pypi/vobject/0.8.1c] for vcard parsing.

In the future we hope to use dulwich[http://pypi.python.org/pypi/dulwich/0.8.7] for git interaction
