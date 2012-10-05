##########
# yuic file compressing handler
##########

# possibly this should somehow be elsewhere?
from marlinespike.hull import ExternalHandler
from marlinespike.cargo import external_print_output

import inspect
import os.path
plugin_dir, _ = os.path.split(inspect.stack()[0][1])
yuic_jar = os.path.abspath(os.path.join(\
    plugin_dir,'external','yuic','yuicompressor-2.4.7.jar'))

class yuic_js(ExternalHandler):
    command = 'java'
    #fallback = copy_file

    def run(self, inputfile, outputfile, context):
        external_print_output(self.command,'-jar', yuic_jar, \
                              inputfile, '-o', outputfile)

_file_handlers = {'.js': yuic_js()}
