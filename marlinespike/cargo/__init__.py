""" marlinespike/cargo/__init__.py
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

    In marlinespike terminology, files are 'cargo'.

    Cargo is dealt with by cargo handlers.

    Frequently, cargo is just handed to an external handler to deal with.

    You probably now know enough to understand this module.
"""

import os.path
import shutil
import subprocess  # for external commands.
from marlinespike.useful import *

class CargoHandler(object):
    #required methods for cargo handlers to define:
    # run(self, inputfile, outputfile, context)
    # make_outputfile_name(self, inputfile, context)

    def make_outputfile_name(self, inputfile, context):
        return os.path.join(context['_output_dir'], inputfile)

    def file_done(self, inputfile, outputfile, context):
        return file_newer_than(inputfile, outputfile)

    def process_file(self, inputfile, context):
        outputfile = self.make_outputfile_name(inputfile, context)

        if self.file_done(inputfile, outputfile, context):
            return

        logging.info(''.join([self.__name__,':',inputfile,'->', outputfile]))
        self.run(inputfile, outputfile, context)

class ExternalHandler(CargoHandler):
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

    def __init__(self):
        ''' this happens at plugin registration.  long before it sees a file! '''
        if not shell_command_exists(self.command):
            if not self.fallback:
                self.run = self.no_command
            else:
                logging.warn('You don\'t have "{}" in your $PATH. \n'
                             'so using "{}" handler instead.'.format(
                                 self.command, self.fallback.__name__))
                self.run = self.fallback.run.__get__(self)

    def process_file(self, inputfile, context):
        outputfile = self.make_outputfile_name(inputfile, context)

        if self.file_done(inputfile, outputfile, context):
            return

        logging.info(''.join([self.command, ':', inputfile, '->', outputfile]))
        return self.run(inputfile, outputfile, context)


    def no_command(self, inputfile, outputfile, context):
        ''' this is a 'run' function for when the command isn't found. '''
        logging.error('Oh no! you need "{}" in your $PATH!\n'
                      'So cannot process "{}".\n'.format(self.command, inputfile))
        exit(2) # something not found

# three 'boiler plate reduction' functions:

def external_print_output(*args):
    return subprocess.check_call(args)

def external_hide_output(*args):
    noise = subprocess.check_output(args)

def external_use_output(outputfile, *args):
    with open(outputfile,'w') as f:
        subprocess.check_call(args, stdout=f)

######################################

# Now for some actual handlers.
# (these are the reeeeally simple basic ones, plus a couple of fun ones.)



class echo_inputfile(CargoHandler):
    def run(self, inputfile, outputfile, context):
        print os.path.join(context['_output_dir'], inputfile)

class copy_file(CargoHandler):
    def run(self, inputfile, outputfile, context):
        shutil.copy2(inputfile, outputfile)

#       one thing to remember, there may be minifying later on in the chain,
#       i.e. running uglifyjs or the closure compiler on .js files in the deploy
#       stage, post-marlinespike.  we don't want the source files being messed up
#       by that.

class hardlink_file(CargoHandler):
    def run(self, inputfile, outputfile, context):
        os.link(inputfile, outputfile)

class symlink_file(CargoHandler):
    def run(self, inputfile, outputfile, context):
        os.symlink(inputfile, outputfile)


#################
#
# Some external 'minifying' handlers
#
#################

class pngcrush(ExternalHandler):
    command = 'pngcrush'
    fallback = copy_file

    def run(self, inputfile, outputfile, context):
        external_hide_output(self.command, inputfile, outputfile)


