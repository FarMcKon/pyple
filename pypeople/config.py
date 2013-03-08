from __future__ import (
    unicode_literals, print_function, with_statement, absolute_import)
import os
import json

"""
pypepope/config.py
Contains tools for pypeople configuration. The pypeople configuration attempts
to load from ~/.pypeople file first. If that does not exist, config assumes
the current directory to be the vcard_directory, and saves no config file

config dict contains 3 values:
    vcard_dir: directory to find vcards in
    cfg_file: configuration file, if 'none' vcard_dir is the local dir
    cfg_file_version: the version of vcard the config file is from/for
"""

_g_config = None  # internal singleton, always load via configs via *get_config()*


def is_valid_config_json(rawData):
    return True  # TODO: make a real json test here someday


def has_config_file(configFilename='~/.pypeople'):
    """ quick check for config file existing. """
    if configFilename is None:
        configFilename = '~/.pypeople'
    return os.path.isfile(os.path.expanduser(configFilename))


def get_config():
    """ load config, assuming it exists. If no config, sets
    some basic values into the global config object """
    global _g_config
    if _g_config is not None:
        logging.debug("reusing singleton config")
        return _g_config  # already loaded, reuse singleton

    cfg_file = '~/.pypeople'
    if not has_config_file(cfg_file):
        _g_config = {}
        _g_config['vcard_dir'] = os.getcwd()
        _g_config['cfg_file'] = None
        _g_config['cfg_file_version'] = '1.0'
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
