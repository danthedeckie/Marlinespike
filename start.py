from os import chdir, listdir, getcwd 
from os.path import isfile, isdir, exists
import json
from glob import glob

import handlers


_FILE_HANDLERS = {
            '.mustache': handlers.mustache_handler,
    ('.markdown','.md'): handlers.markdown_handler,
                  '.js': handlers.echo_filename,
                   None: handlers.echo_filename # Default
    }

_HIDE_ME_PREFIX = '_'
_DEFAULT_CONFIG = {
        '_configfile_name': _HIDE_ME_PREFIX + 'config.json',
        '_file_handlers':_FILE_HANDLERS
        }

def exclude_test(filename):
    """ This is a function so it can be expanded later without refactoring... """
    return False if filename[0] == _HIDE_ME_PREFIX else True

def do_config(where, previous_context):
    if not exists(previous_context['_configfile_name']):
        return previous_context

    with open(previous_context['_configfile_name']) as f:
        new_context = dict(previous_context.items() + json.load(f).items())

    return new_context    

def endswithwhich(search_in, suffixes):
    """ Takes a string and a list of suffixes to test against.
        Returns either the suffix at the end of search_in, or
        else None.  If you give a string as suffixes, it also
        works. Within the list, you can have tuples of multiple
        options too. """
    if type(suffixes) is list:
        for suffix in suffixes:
            if search_in.endswith(suffix):
                return suffix
    elif type(suffixes) is str:
        return suffixes if search_in.endswith(suffixes) else None
    return None

def do_file(filename, context):
    ff = context['_file_handlers']
    ff[endswithwhich(filename, ff.keys())](filename, context)

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
