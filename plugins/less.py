""" less css plugin: 0.0.1

    Note: there seem to be 2 versions of "lessc" around.  If you have the wrong one,
    there may be problems.

"""

def less_handler(filename, context):
    with open(context['_output_basename'] + '.css','w') as f:
        subprocess.call(['lessc', filename], stdout=f)

context['_file_handlers']['.less'] = less_handler
