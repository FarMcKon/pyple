
#!/usr/bin/env python
from __future__ import ( unicode_literals, print_function, with_statement, absolute_import )

import sys
import getopt
import getpass
import atom


try:
    import gdata.contacts.client
    import gdata.contacts.data # you might also need atom.data, gdata.data
except ImportError as e:
    print("No gdata! Prompting gdata install")
    import gdata_install
    if gdata_install.fetch_gdata():
        exit(-5)
    #    gdata_install
    exit(-3)

# OMGZ, gdata might be working now
# based on contacts_example.py from 
# http://gdata-python-client.googlecode.com/hg-history/d2fb9bfbba3bd2212e4e9741734533a2236edbb4/samples/contacts/contacts_example.py
class ContactsFetcher(object):
  """ContactsFetcher object demonstrates operations with the Contacts feed."""

  def __init__(self, email, password):
    """Constructor for the ContactsFetcher object.
    
    Takes an email and password corresponding to a gmail account to
    demonstrate the functionality of the Contacts feed.
    
    Args:
      email: [string] The e-mail address of the account to use for the sample.
      password: [string] The password corresponding to the account specified by
          the email parameter.
    
    Yields:
      A ContactsFetcher object used to run the sample demonstrating the
      functionality of the Contacts feed.
    """
    self.gd_client = gdata.contacts.client.ContactsClient(source='GoogleInc-ContactsPythonSample-1')
    self.gd_client.ClientLogin(email, password, self.gd_client.source)


  def PrintPaginatedFeed(self, feed, print_method):
    """ Print all pages of a paginated feed.
    
    This will iterate through a paginated feed, requesting each page and
    printing the entries contained therein.
    
    Args:
      feed: A gdata.contacts.ContactsFeed instance.
      print_method: The method which will be used to print each page of the
          feed. Must accept these two named arguments:
              feed: A gdata.contacts.ContactsFeed instance.
              ctr: [int] The number of entries in this feed previously
                  printed. This allows continuous entry numbers when paging
                  through a feed.
    """
    ctr = 0
    while feed:
      # Print contents of current feed
      ctr = print_method(feed=feed, ctr=ctr)
      # Prepare for next feed iteration
      next = feed.GetNextLink()
      feed = None
      if next:
        if self.PromptOperationShouldContinue():
          # Another feed is available, and the user has given us permission
          # to fetch it
          feed = self.gd_client.GetContacts(uri=next.href)
        else:
          # User has asked us to terminate
          feed = None

  def PromptOperationShouldContinue(self):
    """ Display a "Continue" prompt.
    
    This give is used to give users a chance to break out of a loop, just in
    case they have too many contacts/groups.
    
    Returns:
      A boolean value, True if the current operation should continue, False if
      the current operation should terminate.
    """
    while True:
      input = raw_input("Continue [Y/n]? ")
      if input == 'N' or input == 'n':
        return False
      elif input == 'Y' or input == 'y' or input == '':
        return True

  def fetch_contacts_to_vcards(self):
    """fetch all contacts to vcard files, etc"""
    feed = self.gd_client.GetContacts()
    self.PrintPaginatedFeed(feed, self.PrintContactsFeed2)

  def ListAllContacts(self):
    """Retrieves a list of contacts and displays name and primary email."""
    feed = self.gd_client.GetContacts()
    
    self.PrintPaginatedFeed(feed, self.PrintContactsFeed)
  
  def PrintContactsFeed(self, feed, ctr):
    if not feed.entry:
      print('\nNo contacts in feed.\n')
      return 0
    for i, entry in enumerate(feed.entry):
      if not entry.name is None:
        family_name = entry.name.family_name is None and " " or entry.name.family_name.text
        full_name = entry.name.full_name is None and " " or entry.name.full_name.text
        given_name = entry.name.given_name is None and " " or entry.name.given_name.text
        print('\n%s %s: %s - %s' % (ctr+i+1, full_name, given_name, family_name))
      else:
        print('\n%s %s (title)' % (ctr+i+1, entry.title.text))
      if entry.content:
        print('    %s' % (entry.content.text))
      for p in entry.structured_postal_address:
        print('    %s' % (p.formatted_address.text))
      # Display the group id which can be used to query the contacts feed.
      print('    Group ID: %s' % entry.id.text)
      # Display extended properties.
      for extended_property in entry.extended_property:
        if extended_property.value:
          value = extended_property.value
        else:
          value = extended_property.GetXmlBlob()
        print('    Extended Property %s: %s' % (extended_property.name, value))
      for user_defined_field in entry.user_defined_field:
        print('    User Defined Field %s: %s' % (user_defined_field.key, user_defined_field.value))
    return len(feed.entry) + ctr

  def PrintContactsFeed2(self, feed, ctr):
    print("PrintContactsFeed2!")
    if not feed.entry:
      print('\nNo contacts in feed.\n')
      return 0
    for i, entry in enumerate(feed.entry):
      if not entry.name is None:
        family_name = entry.name.family_name is None and " " or entry.name.family_name.text
        full_name = entry.name.full_name is None and " " or entry.name.full_name.text
        given_name = entry.name.given_name is None and " " or entry.name.given_name.text
        print('\n%s %s: %s - %s' % (ctr+i+1, full_name, given_name, family_name))
      else:
        print('\n%s %s (title)' % (ctr+i+1, entry.title.text))
      if entry.content:
        print('    %s' % (entry.content.text))
      for p in entry.structured_postal_address:
        print('    %s' % (p.formatted_address.text))
      # Display the group id which can be used to query the contacts feed.
      print('    Group ID: %s' % entry.id.text)
      # Display extended properties.
      for extended_property in entry.extended_property:
        if extended_property.value:
          value = extended_property.value
        else:
          value = extended_property.GetXmlBlob()
        print('    Extended Property %s: %s' % (extended_property.name, value))
      for user_defined_field in entry.user_defined_field:
        print('    User Defined Field %s: %s' % (user_defined_field.key, user_defined_field.value))
    return len(feed.entry) + ctr


 

def main():
  """Demonstrates use of the Contacts extension using the ContactsSample object."""
  # Parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], '', ['user=', 'pw='])
  except getopt.error, msg:
    print('python contacts_example.py --user [username] --pw [password]')
    sys.exit(2)

  user = ''
  pw = ''
  # Process options
  for option, arg in opts:
    if option == '--user':
      user = arg
    elif option == '--pw':
      pw = arg


  while not user:
    print('NOTE: Please run these tests only with a test account.')
    user = raw_input('Please enter your username: ')
  while not pw:
    pw = getpass.getpass()
    if not pw:
      print('Password cannot be blank.')



  try:
    fetcher = ContactsFetcher(user, pw)
    #fetcher.ListAllContacts()
    fetcher.fetch_contacts_to_vcards()
  except gdata.client.BadAuthentication:
    print('Invalid user credentials given.')
    return

if __name__ == '__main__':
    main()
