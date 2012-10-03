"""
    TODO - some kind of page caching system, so the page data
           can be read once when first needed, so I could get the metadata
           from the pages themselves to print here, without replicating
           effort.
"""


def date_from_file(filename, timeformat='%Y%m%d'):
    """ Tries to construct a time from a file(name).  If it can't,
    then it returns the last modified time of the file. """

    from time import strptime, gmtime, strftime
    date_length = len(strftime(timeformat, gmtime()))
    try:
        return strptime(filename[0:date_length], timeformat)
    except:
        return gmtime(os.path.getmtime(filename))

def blog_page(context):
    ''' 
    This function gets called after a page has been rendered from markdown, if the
    'blog' plugin is running (in the page's directory).
    It dumps the appropriate info into the '_cache/blog.filename'
    (replace filename, of course).  Later on, once we actually want a list (say)
    of all the files, we can read the data from these dumps really quickly.
    '''
    global date_from_file
    from time import strftime
    import json
    # file to dump the cache into:
    cachefile = os.path.join(context['_cache_dir'],'blog.'+context['_original_inputfile'])

    # check if there already is an up-to-date cachefile, 
    # if so, don't bother updating it.
    if os.path.exists(cachefile):
        if os.path.getmtime(cachefile) \
        > os.path.getmtime(context['_original_inputfile']):
            return True
        else:
            os.unlink(cachefile)

    # open the cachefile, and dump the current context data into it.
    with open(cachefile,'wb') as f:
        if 'date' in context:
            date = context['date']
        else:
            # format they want the date to end up:
            blog_date_format = context.get('_blog_date_format','%Y-%m-%d')
            # format to read from filename:
            blog_filedate_format = context.get('_blog_filedate_format', '%Y%m%d')

            date = strftime(blog_date_format,
                date_from_file(context['_original_inputfile'], blog_filedate_format))
        full_body = context.get('body','')
        json.dump ( {
            'title': context.get('title',''),
            'description': context.get('description',''),
            'tags': context.get('tags',[]),
            'category': context.get('category',''),
            'filename': context['_output_basename'] + context['_template_extn'],
            'blog_more_text': context.get('_blog_more_text','...'),
            'blog_more_class': context.get('_blog_more_class','blog_more'),
            'body': full_body[0:full_body.find('<!-- _BLOG_MORE -->')],
            'date': date,
            }, f)

def blog_listing(path="blog", template=None, context=None, **kwargs):
    """
    This is what actually displays the shortened list of blogposts.  You should
    specify a template.  This is used by putting a <% blog_listing template="blah" %>
    tag plugin wherever you want it.  As well as the expected fields (title, body, date)
    there will also be a 'url' field, which gives a relative link from the current 
    page to the blogpost.
    """
    from marlinespike.cargo.markdown_handler import _get_template
    import json
    from urllib import quote
    import pystache
    posts_context = {'posts': []}

    for post_cache in glob(os.path.join(context['_cache_dir'],path+'.*')):
        with open(post_cache,'rb') as f:
            posts_context['posts'].append(json.load(f))

    # makes a relative url from the current path to another output file:
    make_url = lambda p: quote(os.path.relpath(p, context['_output_dir']))

    # now do it for all posts:
    for post in posts_context['posts']:
        post['url'] = make_url(post['filename'])

    # add the general context:
    posts_context.update(context)

    # render the output, and send it back:
    return pystache.render(_get_template(template, posts_context), posts_context)


def blog_readmore(**kwargs):
    ''' <% more %> is used to say that a blogpost should only continue on it's
    'real' page, and not on listings. This works a little 'hackily' at the moment,
    by using a magic <!-- comment --> tag, which isn't great, but works just fine. '''
    return '<!-- _BLOG_MORE -->'

markdown_handler.register_tag_plugin('more', blog_readmore)
markdown_handler.register_tag_plugin('blog_listing', blog_listing)
markdown_handler.register_post_plugin('blog_dir', blog_page)

