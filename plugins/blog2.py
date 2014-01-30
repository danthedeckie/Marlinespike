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

        <plugin name="blog_listing" template="templatename" \>

    where you set templatename to whatever template you want to use for
    displaying posts in this page.  The template file can look something like:

    {% for post in posts %}
        <h3><a href="{{post.url}}">{{post.title}}</a></h3> - {{post.date}}
        {{ post.body }}
        <a href="{{post.url}}">{{post.blog_more_text|safe}}</a>
        <hr />
    {% endfor %}

    in a 'post' file, you can put a 'read more' marker:

    <!-- MORE -->

    then posts displayed in a {% for post in posts %}
    block will cut off at that point.



"""
from marlinespike.cargo.markdown_handler import _get_template, DeferPlugin

from time import strptime, gmtime, strftime, mktime
import datetime
import os
from urllib import quote
import logging

from dictlitestore import DictLiteStore, NoJSON

log = logging.getLogger(__file__)
__cachedb = ''
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

    

###################################
#
# The actual plugin functions (entry points)
#
###################################

def blog_page(context):
    '''
    This function gets called after a page has been rendered from markdown, if the
    'blog' plugin is running (in the page's directory).
    It injects a few extra fields into the context, which are useful for
    queries, etc, later on.  Some of this may end up moving across to the
    main markdown handler, later on...
    '''
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

    context['_before_more'] = context['body'].find('<!-- MORE -->')
    context['date'] = date_str
    context['_year'] = date.tm_year
    context['_month'] = date.tm_mon
    context['_day'] = date.tm_mday
    context['_sortable_date'] = strftime('%Y%m%d', date)

def blog_listing(path="blog",
                 template=None,
                 order=(('_sortable_date',u'DESC'),),
                 limit=None,
                 tags='',
                 context=None, **kwargs):
    """
    This is what actually displays the shortened list of blogposts.  You should
    specify a template.  This is used by putting a
    <plugin name="blog_listing" template="blah" \>
    tag plugin wherever you want it.  As well as the expected fields (title,
    body, date) there will also be a 'url' field, which gives a relative link
    from the current page to the blogpost.
    """
    global __cachedb

    if not context['_passno'] == 1:
        raise DeferPlugin()

    posts_context = {'posts': []}

    __cachedb = os.path.join(context['_cache_dir'], 'main.db')

    log.info("reading from: %s",__cachedb)

    tag_filters = []

    for t in searchable_tags(tags.split(',')):
        tag_filters.append( ('_searchable_tags','LIKE', NoJSON('%' + t + '%')))

    with DictLiteStore(__cachedb, 'pages') as s:
        posts_context['posts'] = s.get(*tag_filters, order=order) # TODO: filtering?
        log.info('%i posts', len(posts_context['posts']))

    # makes a relative url from the current path to another output file:
    make_url = lambda p: quote(os.path.relpath(p, context['_output_dir']))

    # now do it for all posts:
    for post in posts_context['posts']:
        post['url'] = make_url(post['_output_basename'] + post['_template_extn'])

    # add the general context:
    posts_context.update(context)

    # render the output, and send it back:
    templ = _get_template(template, posts_context)
    return templ.render(posts_context)

def jinja_blogposts(*query):
    with DictLiteStore(__cachedb,'pages') as store:
        return store.get(*query)


_tag_plugins = {'blog_listing': blog_listing }
_post_plugins = {'blog_dir' : blog_page}
_context = {'post_query' : jinja_blogposts}
