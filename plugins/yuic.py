##########
# yuic file compressing handler
##########

# possibly this should somehow be elsewhere?
import inspect
import os.path
plugin_dir, _ = os.path.split(inspect.stack()[0][1])
yuic_jar = os.path.abspath(os.path.join(\
    plugin_dir,'external','yuic','yuicompressor-2.4.7.jar'))

class yuic_js(external_handler):
    command = 'java'
    #fallback = copy_file

    def run(self, inputfile, outputfile, context):
        global yuic_jar
        external_print_output(self.command,'-jar', yuic_jar, \
                              inputfile, '-o', outputfile)

context['_file_handlers']['.js'] = yuic_js()
