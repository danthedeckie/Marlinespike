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

    ---


"""

import os.path
import commands
import logging
import json
import yaml
import copy

# TODO: sort this out.  I'm sure there is a better way to use this module.
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
# a bit hacky colouring the output
logging.addLevelName( logging.WARNING,
    "\033[1;31m%s\033[0;m" % logging.getLevelName(logging.WARNING))
logging.addLevelName( logging.ERROR,
    "\033[1;41m%s\033[0;m" % logging.getLevelName(logging.ERROR))
logging.addLevelName( logging.INFO,
    "\033[0;m%s" % logging.getLevelName(logging.INFO))

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


def exclude_test(filename, hide_prefix):
    if filename.startswith('.git') \
    or filename.endswith('.swp') \
    or filename == '.DS_Store' \
    or filename.startswith(hide_prefix):
        return False
    else:
        return True


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
        logging.error('Oh no! You need "'+ commandname+'" in your path!')
        exit(2)

def readfile_with_jsonheader(inputfile):
    """ Load a (text) file, and if it starts with '-j-', parse until '\n---\n'
        as JSON metadata, and then return ( rest_of_the_file, metadata ), or
        if there is no -j-, return ( full_file_text, {} ) """
    context = {}

    with open(inputfile) as f:
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
                    except Exception as e:
                        logging.error('Bad JSON header at the top of:' + inputfile)
                        logging.error(str(e.message))
                        exit(1)
                    break
        else:
            f.seek(0)
        return (f.read(), context)

def readfile_splitat(filename, breakstring, ignore_if_starts_with=True):
    """ Read a text file, splitting at the first instance of $breakstring.
        useful for splitting a document into header (json or yaml) and content. """
    before_lines = []
    with open(filename,'r') as f:
        while True:
            line = f.readline()
            if not line:
                logging.debug('end of file while still reading header!')
                # End of File... which means that there isn't any header block!
                return ('', ''.join(before_lines))
            elif line != breakstring:
                logging.debug('normal line: "%s"',line)
                # Normal line, not the breakstring.
                before_lines.append(line)
            else:
                logging.debug('other! %s', line)
                # we've found the breakstring.
                if ignore_if_starts_with and before_lines == []:
                    # however, we're at the beginning of the file.  So ignore it.
                    continue
                # return the header as a header, and the rest as the rest.
                return (''.join(before_lines), f.read())

    raise Exception('We should never have got here. This is BAD.')

def readfile_with_json_or_yaml_header(inputfile):
    header, content = readfile_splitat(inputfile, '---\n')
    context = {}
    if header:
        if header[:3] == '-j-':
            # json header.
            try:
                context = json.loads(header[3:])
                context['_metadata_type'] = 'json'
            except Exception as e:
                logging.error('Bad JSON header at the top of:' + inputfile)
                logging.error(str(e.message))
                exit(1)
        else:
            # maybe YAML header?
            try:
                context = yaml.safe_load(header)
                context['_metadata_type'] = 'yaml'
            except Exception as e:
                # at this point, we have no real indication that there *is* a header.
                # either it's malformed YAML, or else it's not a header at all, so
                # we'll just dump it to the content, and hope it's not YAML.
                #       return (header + content, HeaderMetaDict())
                context.datatype = 'No JSON or YAML'
                content = header + content
    return (content, context)

def dictmerge(basedict, additions_dict):
    ''' create a new Dict by copy/merging an old one with a new one.
        WITH THIS ADDITION:
        any keys in the new dict with '+' or '-' at the end of them are treated
        as append/remove commands (particually for values which are lists)

        >>> dictmerge({'a':[1,21]},{'a+':[42], 'a-':[1],'b':'hi'})
        {'a':[21,42],'b':'hi'}

        and likewise for a-. '''

        # TODO!
    new_dict = copy.deepcopy(basedict)

    for key, val in additions_dict.items():
        if key.endswith('+'):
            realkey = key[:-1]
            # ADD items:
            if not realkey in new_dict:
                # This is entirely new:
                new_dict[realkey] = val
            elif isinstance(new_dict[realkey], list):
                # We're appending to a list.
                if isinstance(val, list):
                    new_dict[realkey] += val
                else:
                    new_dict[realkey].append(val)
            elif isinstance(new_dict[realkey], dict):
                # We're appending to a dict:
                if isinstance(val, dict):
                    new_dict[realkey].update(val)
                else:
                    raise KeyError('Invalid type for dictmerge:' +
                                   key + ',' + val + ',' + new_dict[realkey])
            else:
                # OK, just add it.
                try:
                    # first try simple add:
                    new_dict[realkey] += val
                except TypeError:
                    # ok, then try forcing the type:
                    try:
                        new_dict[realkey] += type(new_dict[realkey])(val)
                    except:
                        raise TypeError('"{}" cannot add {}{} to {}{}'.format(
                            realkey, val, type(val),
                            new_dict[realkey], type(new_dict[realkey]),
                            ))

        elif key.endswith('-'):
            realkey = key[:-1]
            # REMOVE items;

            if not realkey in new_dict:
                # It's already not here!
                pass
            elif isinstance(new_dict[realkey], list):
                # Remove from a list:
                if isinstance(val, list):
                    [new_dict[realkey].remove(v) for v in val]
                else:
                    new_dict[realkey].remove(v)
            elif isinstance(new_dict[realkey], dict):
                # Remove from a dict:
                if isinstance(val, dict):
                    # remove a dict specifying keys?
                    # TODO
                    print 'Trying to remove: ', key, ' from ', new_dict
                    raise TypeError('remove-by-dict not implemented. Sorry!')
                elif isinstance(val, list):
                    # remove a list of keys - don't fail if non-existant
                    [new_dict[realkey].pop(k, None) for k in val]
                else:
                    # remove a single key
                    new_dict[realkey].pop(val, None)
            else:
                # Remove whole value.
                new_dict.remove(realkey)
        else:
            # Normal key.  Replace.
            new_dict[key] = val

    return new_dict
