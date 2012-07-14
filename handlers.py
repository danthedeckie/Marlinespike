""" handlers.py
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
import shutil
import subprocess  # for external commands.
from useful import *
from handler_markdown import markdown

class echo_inputfile(handler):
    def run(self, inputfile, outputfile, context):
        print os.path.join(context['_output_dir'], inputfile)

class copy_file(handler):
    def run(self, inputfile, outputfile, context):
        shutil.copy2(inputfile, outputfile)

##       one thing to remember, there may be minifying later on in the chain,
##       i.e. running uglifyjs or the closure compiler on .js files in the deploy
##       stage, post-marlinespike.  we don't want the source files being messed up
##       by that.

class hardlink_file(handler):
    def run(self, inputfile, outputfile, context):
        os.link(inputfile, outputfile)

class symlink_file(handler):
    def run(self, inputfile, outputfile, context):
        os.symlink(inputfile, outputfile)


#################
#
# Some external 'minifying' handlers
#
#################

class pngcrush(external_handler):
    command = 'pngcrush'
    fallback = copy_file

    def run(self, inputfile, outputfile, context):
        external_hide_output(self.command, inputfile, outputfile)

class yuic_js(external_handler):
    command = 'yuic'
    fallback = copy_file

    def run(self, inputfile, outputfile, context):
        external_print_output(self.command, inputfile, '-o', outputfile)
