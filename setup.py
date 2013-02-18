# setup.py for pypeople 
#
# Direct install (all systems):
#   "python setup.py install"
#
# For Python 3.x use the corresponding Python executable,
# e.g. "python3 setup.py ..."
from __future__ import ( unicode_literals, with_statement, absolute_import )


#New Hotness for distrbuting
try:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
except ImportError:
    from setuptools import setup

#old bustedness for distrubtiong

import sys


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
    suffix ='' 


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

if sys.version >= '2.3':
  #import pypeople  version = pypeople.__version__ 
  ##^ causes some kind of dependnecy-implosion on some systems
  import re, os
  version = re.search(
        "__version__.*'(.+)'",
        open(os.path.join('pypeople','pypeople.py')).read()).group(1)
setup(
    name = "pypeople" + suffix,
    description = "Commandline vCard editor in Python, with git syncing",
    version = version,
    author = "Far McKon",
    author_email = "farMcKon@gmail.com",
    url = "http://github.com/farmckon/pyple",
    packages = find_packages(),
    install_requires=['vobject>=0.7',],
    #dependency_links = ['http://pypi.python.org/pypi/vobject'],
    #packages= ['pypeople',],
    #package_dir={'pypeople': 'pypeople'},
    #package_data={'pypeople': ['*.py']},
    license = "AGPL",
    long_description = "Commandline vcard editor for address book management, written in Python",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
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
