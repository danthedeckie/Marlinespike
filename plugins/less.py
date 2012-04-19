def less_handler(filename, context):
    with open(context['_output_basename'] + '.css','w') as f:
        subprocess.call(['lessc', filename], stdout=f)

context['_file_handlers']['.less'] = less_handler
