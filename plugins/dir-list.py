"""
    Quick demo plugin of how to do a directory listing (needed for
    my personal site).  This found a bug! (noted in TODO.md)

    TODO - some kind of page caching system, so the page data
           can be read once when first needed, so I could get the metadata
           from the pages themselves to print here, without replicating
           effort.
"""

def dir_pages(where=".", files="*.markdown", html='', **kwargs):
    text = ""
    for page in glob(os.path.join(where,files)):
        name, a = os.path.splitext(os.path.basename(page))
        text += html.format(url=page.replace(".markdown",".html"), name=name)
    return text

markdown_handler.register_tag_plugin('dir',dir_pages)


