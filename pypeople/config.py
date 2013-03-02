from __future__ import ( unicode_literals, print_function, with_statement, absolute_import )
import os
import json
"""
 Contains config system files for pypeople tool
"""

_g_config = None # for singleton, always load via *get_config*

def is_valid_config_json(rawData):
    return True

#@memoize
def has_config_file(configFilename=None):
    """ quick check for config file existing. """
    file = configFilename if configFilename else '~/.pypeople'
    return os.path.isfile(os.path.expanduser(file))

def get_config() :
    """ load config, assuming it exists. If no config, sets
    some basic values into the global config object """
    global _g_config
    if _g_config != None:
        return _g_config #already loaded, reuse singleton

    cfg_file = '~/.pypeople'
    if not has_config_file(cfg_file):
        _g_config = {}
        _g_config['vcard_dir'] = os.getcwd()
        _g_config['cfg_file'] = None
        _g_config['cfg_version'] = utils.__version_info__
        return _g_config

    cfg_full = os.path.expanduser(cfg_file)
    with open(cfg_full, 'rb') as fh:
        rawdata = fh.read()
        data = json.loads(rawdata)
        if is_valid_config_json(data):
            _g_config = data
            return _g_config 

    print("unspecified load config error")
    return None 
  
