# PyPeople: Command Line AddressBook in Python

PyPeople is a python command-line address book, with optional git-syncing.

Inspired by ppl (ruby commandline addressbook) and with some vacation time to spare, I've put together pypeople. 


# Overview
PyPeople makes it easy to create or edit vcf files. If you don't have a ~/.pypeople file (created by the 'init' command), it will list/edit/create vCard .vcf files in the directroy pypeople is running in.

If you do run 'init' you can create a config file (stored at ~/.pypeople) to specify a vCard contact directory, and an optional git repository to sync contacts to/from.

## help
   pypeople help 
Displays help commands for the most common usage

## init 
    pypeople init ~/Contacts
    pypeople init ~/Contacts git@github.com/User/PrivateContacts
Creates a config file for pypeople at ~/.pypeople with the given optoins. The first option is your vcard contacts directory, the second is an optional git repository which sync will use to push/pull contact info from.

f you never run this command, pypeople will assume the directroy you are in is your contacts, and the 'sync' command will be disabled.
 
## add  
    pypeople add jrand "J Random Hack"
Creates a vcard 'jrand' containing the name (and email/phone if specified) entered.


## See Also 
vobject 0.8.1c
dulwich
