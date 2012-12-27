# setup.py for pypl 
#
# Direct install (all systems):
#   "python setup.py install"
#
# For Python 3.x use the corresponding Python executable,
# e.g. "python3 setup.py ..."

#New Hotness for distrbuting
from distribute_setup import use_setuptools
use_setuptools()

#old bustedness for distrubtiong
#from ez_setup import use_setuptools
#use_setuptools()

import sys

from distutils.core import setup
from setuptools import setup, find_packages

if sys.version_info >= (3, 0):
    try:
        from distutils.command.build_py import build_py_2to3 as build_py
        from distutils.command.build_scripts import build_scripts_2to3 as build_scripts
    except ImportError:
        raise ImportError("build_py_2to3 not found in distutils - it is required for Python 3.x")
    suffix = "-py3k"
else:
    from distutils.command.build_py import build_py
    from distutils.command.build_scripts import build_scripts
    suffix = ""


if sys.version < '2.3':
    # distutils that old can't cope with the "classifiers" or "download_url"
    # keywords and True/False constants and basestring are missing
    raise ValueError("Sorry Python versions older than 2.3 are no longer"
                     "supported - check http://pyserial.sf.net for older "
                     "releases or upgrade your Python installation.")

# importing version does not work with Python 3 as files have not yet been
# converted.
#~ import serial
#~ version = serial.VERSION

if sys.version >= '2.3' and sys.version < '3.0':
  import pypl 
  version = pypl.__version__

elif sys.version >= 3.0:
  import re, os
  version = re.search(
        "__version__.*'(.+)'",
        open(os.path.join('pypl', '__init__.py')).read()).group(1)


setup(
    name = "pypl" + suffix,
    description = "Commandline vCard editor in Python, with git syncing",
    version = version,
    author = "Far McKon",
    author_email = "farMcKon@gmail.com",
    url = "http://github.com/farmckon/pypl",
    packages = find_packages(),
    license = "AGPL",
    long_description = "Commandline vcard editor for address book management, written in Python",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)'
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        #untested in python 3
#        'Programming Language :: Python :: 3',
#        'Programming Language :: Python :: 3.0',
#        'Programming Language :: Python :: 3.1',
#        'Programming Language :: Python :: 3.2',
        'Topic :: Communications :: Email :: Address Book',
        'Topic :: Software Development :: Libraries',
        'Topic :: Database',
        'Topic :: Utilities',
    ],
    platforms = 'any',
    cmdclass = {'build_py': build_py, 'build_scripts': build_scripts},

    #scripts = ['serial/tools/miniterm.py'],
)
