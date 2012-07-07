"""  useful.py
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
import json

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


def file_already_done(original, new):
    """ very basic check if $new exists, or if $original is newer than $new. """
    return ((os.path.isfile(new)) and 
            os.path.getmtime(original) <= os.path.getmtime(new))

@memoize
def shell_command_exists(commandname):
    # there's probably a better / faster way to do this.
    return commands.getoutput('which ' + commandname) != ''

def need_shell_command(commandname):
    if not shell_command_exists(commandname):
        print('Oh no! You need "'+ commandname+'" in your $PATH!')
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


