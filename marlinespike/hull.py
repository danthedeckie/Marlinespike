#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""  Marlinespike static site generator
     (C) Copyright 2012 Daniel Fairhead

    This file is part of Marlinespike.

    Marlinespike is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Marlinspike is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Marlinespike.  If not, see <http://www.gnu.org/licenses/>.

    (Just in case you're worried, files/sites you create with Marlinespike
     are your property - you don't need to GPL them or worry about legal
     stuff.  You only need to think about this stuff if you plan to redistribute
     Marlinespike itself)

---

hull.py is kind of the main base that everything sits on.  We're not talking
  about funky math shapes here, this is a hull as in a ship's hull.

"""


import sys                       # For UTF-8 settings.
reload(sys)                      # Stupid hack to re-apply UTF-8 if it
                                 # - wasn't loaded originally.
sys.setdefaultencoding('utf-8')  # - Oh for Py3k everywhere.


# External Libs
from os import chdir, listdir, getcwd
import os.path
import json
from glob import glob
import subprocess  # needed for most plugins.
import copy
import traceback

# Internal stuff
import marlinespike.cargo as cargo
from marlinespike.cargo import *
from marlinespike.cargo.markdown_handler import markdown
from marlinespike.useful import endswithwhich, readfile_with_jsonheader, logging, exclude_test

################################
# Default Settings
################################

# markdown_handler is done like this so markdown plugins
# can register themselves with markdown_handler.register_plugin...
# rather than having to hunt through the _FILE_HANDLERS dict for it.
markdown_handler = markdown()

_FILE_HANDLERS = {
    ('.markdown', '.md'): markdown_handler,
                  '.png': cargo.pngcrush(),
                    None: cargo.copy_file()  # Default
    }

_HIDE_ME_PREFIX = '_'

# TODO - move this to a function, or something, so it updates via the _HIDE_ME_PREFIX

_DEFAULT_CONFIG = {
          '_configfile_name': _HIDE_ME_PREFIX + 'config.json',
            '_file_handlers': _FILE_HANDLERS,
               '_output_dir': os.path.join(getcwd(), _HIDE_ME_PREFIX + 'site'),
                '_cache_dir': os.path.join(getcwd(), _HIDE_ME_PREFIX + 'cache'),
             '_template_dir': os.path.join(getcwd(), _HIDE_ME_PREFIX + 'templates'),
            '_template_extn': '.html',
        '_parent_output_dir': getcwd(),
                 '_base_dir': getcwd()
        }


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

#############################
# The big 3
#############################


def do_config(where, previous_context):
    if not os.path.exists(previous_context['_configfile_name']):
        return copy.deepcopy(previous_context)

    with open(previous_context['_configfile_name']) as f:
        try:
            return dict(copy.deepcopy(previous_context).items() + json.load(f).items())
        except Exception as e:
            logging.error('Bad JSON in file:' + previous_context['_configfile_name'])
            logging.error(str(e.message))
            exit(1)

def do_file(filename, context):
    root, ext = os.path.splitext(filename)
    # dicts are mutable in python.  Make a local copy for this
    # file, so that the handler can muck around with it and not
    # break everything else:
    my_context = copy.deepcopy(context)

    # some file-specific settings:
    my_context['_output_basename'] = os.path.join(context['_output_dir'], root)
    my_context['_input_extension'] = ext

    # select the appropriate handler, and run with it:
    handlers = my_context['_file_handlers']
    handlers[endswithwhich(filename, handlers.keys())].process_file(filename, my_context)


def do_dir(where, previous_context):
    return_to = getcwd()
    chdir(where)
    context = do_config(where, previous_context)

    if not '_base_path' in context:
        context['_base_path'] = ''
    else:
        context['_base_path'] += '../'

    context['_output_dir'] = context.pop('_output_dir', os.path.join(context['_parent_output_dir'], where))

    if os.path.exists('_config.py'):
        sys.path.insert(0,os.getcwd())

        # Make _plugins/ directories behave as modules:
        # temp variables to make the next if nicer:
        plugin_dir = _HIDE_ME_PREFIX + 'plugins'
        plugin_modulator = os.path.join(plugin_dir, '__init__.py')

        if os.path.isdir(plugin_dir) and not os.path.exists(plugin_modulator):
            open(plugin_modulator,'wb').close()

        try:
            def do_plugin(filename):
                #global context
                x = __import__(filename, fromlist=True)
                # Here is a list of plugins we import:
                # TODO: functionise/DRY this:
                if '_context' in dir(x):
                    context.update(x._context)
                if '_file_handlers' in dir(x):
                    context['_file_handlers'].update(x._file_handlers)
                if '_tag_plugins' in dir(x):
                    [markdown_handler.register_tag_plugin(tag, func) \
                        for tag, func in x._tag_plugins.items()]
                if '_post_plugins' in dir(x):
                    [markdown_handler.register_post_plugin(tag, func) \
                        for tag, func in x._post_plugins.items()]


            execfile('_config.py')
        except Exception as e:
            logging.error('Error with _config.py in ' + os.getcwd())
            [logging.error(l) for l in traceback.format_exc().splitlines()]
            exit(1)

    if not os.path.exists(context['_cache_dir']):
        os.makedirs(context['_cache_dir'])

    if not os.path.exists(context['_output_dir']):
        os.makedirs(context['_output_dir'])
    elif not os.path.isdir(context['_output_dir']):
        os.rename(context['_output_dir'], context['_output_dir'] + '.prev')
        os.makedirs(context['_output_dir'])

    files_list = []
    for filename in filter(lambda x: exclude_test(x, _HIDE_ME_PREFIX), listdir('.')):

        # Do files after subdirectories...
        if os.path.isfile(filename):
            files_list.append(filename)

        if os.path.isdir(filename):
            # TODO - think.  Is this the best place for this?  I kind of
            # think it should be in do_config ?? I dunno...
            my_parent_output_dir = context['_parent_output_dir']
            my_output_dir = context['_parent_output_dir'] = context.pop('_output_dir')

            do_dir(filename, context)

            context['_parent_output_dir'] = my_parent_output_dir
            context['_output_dir'] = my_output_dir

    [do_file(filename, context) for filename in files_list]
    # return to where we came from before leaving...
    # it's only polite.
    chdir(return_to)

if __name__ == '__main__':
    do_dir(getcwd(), _DEFAULT_CONFIG)
    print("Done.\n")
