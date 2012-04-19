#!/opt/local/bin/python
# External Libs
from os import chdir, listdir, getcwd 
import os.path
import json
from glob import glob
# Internal stuff
import handlers
from useful import *

################################
# Default Settings
################################

_FILE_HANDLERS = {
    ('.markdown','.md'): handlers.markdown_handler,
                  '.js': handlers.copy_file,
                '.less': handlers.less_handler,
                   None: handlers.copy_file # Default
    }

_HIDE_ME_PREFIX = '_'

# TODO - move this to a function, or something, so it updates via the _HIDE_ME_PREFIX

_DEFAULT_CONFIG = {
        '_configfile_name': _HIDE_ME_PREFIX + 'config.json',
        '_file_handlers':_FILE_HANDLERS,
        '_output_dir': os.path.join(getcwd(), _HIDE_ME_PREFIX + 'site'),
        '_template_dir': os.path.join(getcwd(), _HIDE_ME_PREFIX + 'templates'),
        '_template_extn': '.html',
        '_parent_output_dir': getcwd(),
        '_base_dir': getcwd()
        }

##############################
# Function helpers
##############################


def exclude_test(filename):
    """ This is a function so it can be expanded later without refactoring... """
    return False if filename[0] == _HIDE_ME_PREFIX else True

#############################
# The big 3
#############################

def do_config(where, previous_context):
    if not os.path.exists(previous_context['_configfile_name']):
        return previous_context.copy()

    with open(previous_context['_configfile_name']) as f:
        return dict(previous_context.items() + json.load(f).items())


def do_file(filename, context):
    root, ext = os.path.splitext(filename)
    context['_output_basename'] = os.path.join(context['_output_dir'], root)
    context['_input_extension'] = ext

    ff = context['_file_handlers']
    ff[endswithwhich(filename, ff.keys())](filename, context)

    del(context['_output_basename'])
    del(context['_input_extension'])


def do_dir(where, previous_context):
    return_to = getcwd()
    chdir(where)
    context = do_config(where, previous_context)

    context['_output_dir'] = context.pop('_output_dir', os.path.join(context['_parent_output_dir'], where))

    if os.path.exists('_config.py'):
        execfile('_config.py')

    if not os.path.exists(context['_output_dir']):
        os.makedirs(context['_output_dir'])
    elif not os.path.isdir(context['_output_dir']):
        os.rename(context['_output_dir'], context['_output_dir'] + '.prev')


    for filename in filter(exclude_test, listdir('.')):

        if os.path.isfile(filename):
            do_file(filename, context)

        if os.path.isdir(filename):
            # TODO - think.  Is this the best place for this?  I kind of
            # think it should be in do_config ?? I dunno...
            my_parent_output_dir = context['_parent_output_dir']
            my_output_dir = context['_parent_output_dir'] = context.pop('_output_dir')

            do_dir(filename, context)

            context['_parent_output_dir'] = my_parent_output_dir
            context['_output_dir'] = my_output_dir
            


    # return to where we came from before leaving... 
    # it's only polite.
    chdir(return_to)




if __name__ == '__main__':
    do_dir(getcwd(), _DEFAULT_CONFIG)
