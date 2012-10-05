""" scss->css plugin: 0.0.1

"""
from marlinespike.hull import CargoHandler

from scss import Scss
scssc = Scss()

class scss_handler(CargoHandler):

    ''' scss compiler. '''

    def make_outputfile_name(self, filename, context):
        return context['_output_basename'] + '.css'

    def run(self, inputfile, outputfile, context):
        with open(inputfile,'r') as i:
            with open(outputfile,'w') as o:
               o.write(self.scssc.compile(i.read()))

_file_handlers = {'.scss': scss_handler()}
