""" image_magick plugin: v.0.1

    Example: 
    
    in a directory _config.json:

        { "image_magick" :  [
            { "destination" : "thumbnails",
                   "resize" : "214x142" },
            { "destination" : "../medium",
                   "resize" : "640x480" }
        ] }

    will create a directory (in the current directory) called "thumbnails" and copy
    resized versions of all .jpg files in, and a directory called "medium" in the 
    parent directory with resized versions of the same.

    To copy the original files as well, add "copy_originals" into the image_magick
    list:

        { "image_magick" : [ "copy_originals",
            { "destination" ...

    STATUS:

        - Currently only supports the resize tag.  It should be reasonably simple
          to support other tags - in some ways the best would be a generic mapping
          of all options.

    TODO:

        - Support other options
        - different file types, and file conversions
        - site level config as well as / instead of directory level

"""

def image_magick(filename, context):
    if not 'image_magick' in context:
        return handlers.copy_file(filename, context)

    for conversion in context['image_magick']:
        if conversion == "copy_originals":
            handlers.copy_file(filename, context)
            continue

        outputdir = os.path.join(context['_output_dir'], conversion['destination'])

        if not os.path.isdir(outputdir):
            os.makedirs(outputdir)

        subprocess.call(['convert','-resize', conversion['resize'], filename, 
            os.path.join(outputdir,  filename)])

context['_file_handlers']['.jpg'] = image_magick
