"""
    Quick demo plugin of how to do a directory listing (needed for
    my personal site).  This found a bug! (noted in TODO.md)

    TODO - some kind of page caching system, so the page data
           can be read once when first needed, so I could get the metadata
           from the pages themselves to print here, without replicating
           effort.
"""
import os.path
from glob import glob

from marlinespike.cargo.markdown_handler import _get_template

def dir_pages(where=".", files="*.markdown", template='', context=None, **kwargs):
    renderer = _get_template(template, context)

    files = []

    for page in glob(os.path.join(where,files)):
        name, a = os.path.splitext(os.path.basename(page))
        files.append( {
            'name': name,
            'url': page.replace(".markdown",".html")
            })
    print files
    return renderer.render({'files':files})

_tag_plugins = {'dir': dir_pages}


