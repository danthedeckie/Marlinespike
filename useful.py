"""  useful.py -- useful functions and decorators
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

"""

import os.path
import commands
import logging
import json

# TODO: sort this out.  I'm sure there is a better way to use this module.
logging.basicConfig(level=logging.DEBUG)
# a bit hacky colouring the output
logging.addLevelName( logging.WARNING, "\033[1;31m%s\033[1;m" % logging.getLevelName(logging.WARNING))
logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;m" % logging.getLevelName(logging.ERROR))
logging.addLevelName( logging.INFO, "\033[0;m%s" % logging.getLevelName(logging.INFO))

################################
# Generic(ish) Useful Functions
################################

class memoize(object):
    """ v. simple memoizing decorator. """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        return self.func.__doc__

# These should be somewhere else.
# TODO: move handlers etc!

class handler(object):
    #required methods for handlers to define:
    # run(self, inputfile, outputfile, context)
    # make_outputfile_name(self, filename, context)
 
    def make_outputfile_name(self, filename, context):
        return os.path.join(context['_output_dir'], filename)

    def file_done(self, inputfile, outputfile, context):
        return file_newer_than(inputfile, outputfile)

    def process_file(self, inputfile, context):
        outputfile = self.make_outputfile_name(filename, context)

        if self.file_done(inputfile, outputfile, context):
            return

        logging.info(''.join([self.__class__.__name__,':',inputfile,'->' outputfile]))
        self.run(inputfile, outputfile, context)

class external_handler(handler):
    fallback = False
    # required properties by plugins:
    # command = (something like 'pngcrush' or 'cp' ...

    # requried methods:
    # make_outputfile_name(self)
    # run(self)
    
    # set by handler base-class (or over-ridden)
    # inputfile
    # outputfile
    # context

    def __init__():
        ''' this happens at plugin registration.  long before it sees a file! '''
        if not shell_command_exists(self.command):
            if not self.fallback:
                self.run = self.no_command
            else:
                logging.warn('You don\'t have "{}" in your $PATH. \n'
                             'so using "{}" handler instead.'.format(
                                 command, self.fallback.__class__.__name__))
                self.run = fallback.run

    def process_file(self, inputfile, context):
        outputfile = self.make_outputfile_name(filename, context)

        if self.file_done(inputfile, outputfile, context):
            return
        
        logging.info(''.join([self.command, ':', inputfile, '->', outputfile]))
        return self.run(inputfile, outputfile, context)


    def no_command(self, inputfile, outputfile, context):
        ''' this is a 'run' function for when the command isn't found. '''
        logging.error('Oh no! you need "{}" in your $PATH!\n'
                      'So cannot process "{}".\n'.format(command, inputfile))
        exit(2) # something not found
######################################



def endswithwhich(search_in, suffixes):
    """ Takes a string and a list of suffixes to test against.
        Returns either the suffix at the end of search_in, or
        else None.  If you give a string as suffixes, it also
        works. Within the list, you can have tuples of multiple
        options too. """
    if type(suffixes) is list:
        for suffix in filter(lambda x: x, suffixes):
            if search_in.endswith(suffix):
                return suffix
    elif type(suffixes) is str:
        return suffixes if search_in.endswith(suffixes) else None
    return None


def file_newer_than(original, new):
    """ very basic check if $new exists, or if $original is newer than $new. """
    return ((os.path.isfile(new)) and
            os.path.getmtime(original) <= os.path.getmtime(new))

@memoize
def shell_command_exists(commandname):
    # TODO: there's probably a better / faster way to do this.
    return commands.getoutput('which ' + commandname) != ''

def need_shell_command(commandname):
    if not shell_command_exists(commandname):
        print('Oh no! You need "'+ commandname+'" in you path!')
        exit(2)

def readfile_with_jsonheader(filename):
    """ Load a (text) file, and if it starts with '-j-', parse until '\n---\n'
        as JSON metadata, and then return ( rest_of_the_file, metadata ), or
        if there is no -j-, return ( full_file_text, {} ) """
    context = {}

    with open(filename) as f:
        test = f.read(3)
        if test == '-j-':
            json_data = ""
            while True:
                line = f.readline()
                if line is None:
                    break
                elif line != '---\n':
                    json_data += line
                else:
                    try:
                        context = json.loads(json_data.strip())
                    except:
                        raise RuntimeError('Invalid / Unhappy JSON meta data at the top of "' + filename + '"')
                    break
        else:
            f.seek(0)
        return (f.read(), context)


