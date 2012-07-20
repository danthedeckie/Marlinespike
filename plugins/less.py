""" less css plugin: 0.0.3

    Note: there seem to be 2 versions of "lessc" around.  If you have the wrong
          one, there will be problems.  one returns the new CSS to stdout, the
          other requires an inputfile and an outputfile as command arguments.  

    TODO: cope with both.  should be possible by running it w/o args, and 
          checking it's output for '>' or something like that.

"""

class lessc(ExternalHandler):
    ''' lessc compiler, LESS to CSS. '''
    command='lessc'

    def make_outputfile_name(self, filename, context):
        return context['_output_basename'] + '.css'

    def run(self, inputfile, outputfile, context):
        external_use_output(outputfile, self.command, inputfile)

context['_file_handlers']['.less'] = lessc()
