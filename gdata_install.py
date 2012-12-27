#!/usr/bin/env python
from __future__ import ( unicode_literals, print_function, with_statement, absolute_import )

gdata_zip = 'gdata-2.0.17.tar.gz' 
gdata_client_src= 'http://gdata-python-client.googlecode.com/files/' + gdata_zip
def fetch_gdata():
    print("monkey-at-keyboard automation of installing gdata (gdata-python-client)")
    print("open a new terminal")
    print("at that terminal, run 'wget "+gdata_client_src+'"')
    print("when done, run 'tar -xzvf "+ gdata_zip+'"')
    print("then move to the gdata dir by 'cd gdata-2.0.17'")
    print("finally, run the install via 'python ./setup.py install")

