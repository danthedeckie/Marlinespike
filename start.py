from os import chdir, listdir, getcwd 
from os.path import isfile, isdir, exists
#import re
import json
from glob import glob
import pystache
import markdown2

def echo_filename(filename, context):
    print 'ECHO!:'
    print filename

def mustache_handler(filename, context):
    print 'MUSTACHE!:'
    print filename


_FILE_FUNCTIONS = {
    'mustache': mustache_handler,
    'js': echo_filename,
    '_DEFAULT': echo_filename
    }

_HIDE_ME_PREFIX = '_'
_DEFAULT_CONFIG = {
        'configfile_name': _HIDE_ME_PREFIX + 'config.json',
        'file_functions':_FILE_FUNCTIONS
        }

def exclude_test(filename):
    """ This is a function so it can be expanded later without refactoring... """
    return False if filename[0] == _HIDE_ME_PREFIX else True

def do_config(where, previous_context):
    if not exists(previous_context['configfile_name']):
        return previous_context

    with open(previous_context['configfile_name']) as f:
        new_context = dict(previous_context.items() + json.load(f).items())

    return new_context    

def do_file(filename, context):
    # TODO:
    # if file_ending in context['file_functions']:
    #     context['file_functions'][file_ending](filename, context)
    # else:
    #     context['file_functions']['_DEFAULT'](filename, context)
    print filename

def do_dir(where, previous_context):
    return_to = getcwd()
    chdir(where)
    context = do_config(where, previous_context)

    for filename in filter(exclude_test, listdir(where)):

        if isfile(filename):
            do_file(filename, context)

        if isdir(filename):
            do_dir(filename, context)

    # return to where we came from before leaving... 
    # it's only polite.
    chdir(return_to)

if __name__ == '__main__':
    do_dir(getcwd(), _DEFAULT_CONFIG)
