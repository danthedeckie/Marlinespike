"""
    Marlinespike's blogging system!  This is probably the most complex of the plugins
    that you're likely to find.

    TODO: filtering of posts in post_listings
          removing old cache?
          documentation on how best to use this.

    Basic use:

    in your _config.py:

        do_plugin('plugins.blog')

    in the directory that you want to have blog posts in, create a _config.py
    with:

        context['plugins'] = ['blog_dir']

    in the page where you want a list of all blog posts:

        <% blog_listing template="templatename" %>

    where you set templatename to whatever template you want to use for
    displaying posts in this page.  The template file can look something like:

    {% for post in posts %}
        <h3><a href="{{post.url}}">{{post.title}}</a></h3> - {{post.date}}
        {{ post.body }}
        <a href="{{post.url}}">{{post.blog_more_text|safe}}</a>
        <hr />
    {% endfor %}

    in a 'post' file, you can put a 'read more' marker:

    <% more %>

    then posts displayed in a {% for post in posts %}
    block will cut off at that point.



"""
from marlinespike.cargo.markdown_handler import _get_template

from time import strptime, gmtime, strftime, mktime
import datetime
import os
from urllib import quote
import logging

from lib.DictLiteStore import DictLiteStore, NoJSON

log = logging.getLogger(__file__)
####################################################
#
# Functions used by the 'plugin functions' later:
#
####################################################

def date_from_file(filename, timeformat='%Y%m%d'):
    """ Tries to construct a time from a file(name).  If it can't,
    then it returns the last modified time of the file. """

    date_length = len(strftime(timeformat, gmtime()))
    try:
        return strptime(filename[0:date_length], timeformat)
    except:
        return gmtime(os.path.getmtime(filename))


def searchable_tags(inlist):
    ''' takes a list of strings, and returns a list of strings, but each
        is hashed, and surrounded by '_', thus making SQL:
        LIKE %_x_% possible & easy. '''
    return ['_' + str(hash(x)) + '_' for x in inlist]

def context_to_blogcache(context):
    ''' takes a full context dict, and returns a simpler
        dict with just the data we want to put in the blog cache. '''

    # format they want the date to end up:
    blog_date_format = context.get('_blog_date_format','%Y-%m-%d')

    if 'date' in context:
        if isinstance(context['date'], datetime.date):
            date = context['date'].timetuple()
        else:
            date = strptime(context['date'], blog_date_format)

    else:
        # format to read from filename:
        blog_filedate_format = context.get('_blog_filedate_format', '%Y%m%d')

        date = date_from_file(context['_original_inputfile'], blog_filedate_format)

    date_str = strftime(blog_date_format, date)

    full_body = context.get('body','')
    return {
        'title': context.get('title',''),
        'description': context.get('description',''),
        'tags': context.get('tags',[]),
        'searchable_tags': searchable_tags(context.get('tags',[])),
        'category': context.get('category',''),
        'filename': context['_output_basename'] + context['_template_extn'],
        'blog_more_text': context.get('_blog_more_text','...'),
        'blog_more_class': context.get('_blog_more_class','blog_more'),
        'body': full_body[0:full_body.find('<!-- _BLOG_MORE -->')],
        'date': date_str,
        '_year': date.tm_year,
        '_month': date.tm_mon,
        '_day': date.tm_mday,
        '_sortable_date': strftime('%Y%m%d', date),
        'filemtime': os.path.getmtime(context['_original_inputfile']),
        '_original_inputfile': context['_original_inputfile'],
        }


###################################
#
# The actual plugin functions (entry points)
#
###################################

def blog_page(context):
    '''
    This function gets called after a page has been rendered from markdown, if the
    'blog' plugin is running (in the page's directory).
    It dumps the appropriate info into the '_cache/blog.db'
    Later on, once we actually want a list (say)
    of all the files, we can read the data from these dumps really quickly.
    '''
    # file to dump the cache into:
    cachedb = os.path.join(context['_cache_dir'],'blog.db')
    key = "_original_inputfile"
    wherekey = (key,'==', context[key])
    # check if there already is an up-to-date cachefile, 
    # if so, don't bother updating it.
    with DictLiteStore(cachedb, 'pages') as s:
        c = s.get(wherekey)

        if c != [] and c[0]['filemtime'] \
        > os.path.getmtime(context[key]):
            log.debug('%s already in cache!', key)
            return True

        log.debug ('%s not in cache, or needs to be updated.', key)
        #If we got here, then the cache needs updating.
        s.update(context_to_blogcache(context), True, wherekey)


def blog_listing(path="blog", template=None, order=(('_sortable_date',u'DESC'),), limit=None, tags='', context=None, **kwargs):
    """
    This is what actually displays the shortened list of blogposts.  You should
    specify a template.  This is used by putting a
    <% blog_listing template="blah" %>
    tag plugin wherever you want it.  As well as the expected fields (title,
    body, date) there will also be a 'url' field, which gives a relative link
    from the current page to the blogpost.
    """
    posts_context = {'posts': []}
    cachedb = os.path.join(context['_cache_dir'], 'blog.db')

    log.info("reading from: %s",cachedb)

    tag_filters = []


    for t in searchable_tags(tags.split(',')):
        tag_filters.append( ('searchable_tags','LIKE', NoJSON('%' + t + '%')))

    print tag_filters

    with DictLiteStore(cachedb, 'pages') as s:
        posts_context['posts'] = s.get(*tag_filters, order=order) # TODO: filtering?


    # makes a relative url from the current path to another output file:
    make_url = lambda p: quote(os.path.relpath(p, context['_output_dir']))

    # now do it for all posts:
    for post in posts_context['posts']:
        post['url'] = make_url(post['filename'])

    # add the general context:
    posts_context.update(context)

    # render the output, and send it back:
    templ = _get_template(template, posts_context)
    return templ.render(posts_context)


def blog_readmore(**kwargs):
    ''' <% more %> is used to say that a blogpost should only continue on it's
    'real' page, and not on listings. This works a little 'hackily' at the moment,
    by using a magic <!-- comment --> tag, which isn't great, but works just fine. '''
    return '<!-- _BLOG_MORE -->'

_tag_plugins = {'more': blog_readmore,
                'blog_listing': blog_listing }
_post_plugins = {'blog_dir' : blog_page}
