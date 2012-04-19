def image_magick(filename, context):
    if not 'image_magick' in context:
        return handlers.copy_file(filename, context)

    for conversion in context['image_magick']:
        outputdir = os.path.join(context['_output_dir'], conversion['destination'])

        if not os.path.isdir(outputdir):
            os.makedirs(outputdir)

        subprocess.call(['convert','-resize', conversion['resize'], filename, 
            os.path.join(outputdir,  filename)])

context['_file_handlers']['.jpg'] = image_magick
