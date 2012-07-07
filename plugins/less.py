""" less css plugin: 0.0.2

    Note: there seem to be 2 versions of "lessc" around.  If you have the wrong one,
    there may be problems.

"""

@external_handler('lessc')
def less_handler(filename, context):
    """ LESS -> CSS converter. uses the 'lessc' compiler """
    outputfile = context['_output_basename'] + '.css'
    if not file_already_done(filename, outputfile):
        logging.info("Updating:" + filename)
        with open(outputfile, 'w') as f:
            subprocess.check_call(['lessc', filename], stdout=f)


context['_file_handlers']['.less'] = less_handler
