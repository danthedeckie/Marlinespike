import os.path
import re
import pystache
import markdown2
import shutil


def echo_filename(filename, context):
    print os.path.join(context['_output_dir'], filename)
    print filename

def copy_file(filename, context):
    shutil.copy2(filename, os.path.join(context['_output_dir'], filename))

def mustache_handler(filename, context):
    print 'MUSTACHE!:'
    print filename
    print context['_output_basename'] + '.html'

def markdown_handler(filename, context):
    print 'Markdown:'
    print filename
    print context['_output_basename'] + '.html'

###########
# For pystache/markdown files:
###########

# from tests.

#TAB_LENGTH = 4            # expand tabs to this many spaces
ENABLE_ATTRIBUTES = True  # @id = xyz -> <... id="xyz">
SMART_EMPHASIS = 1        # this_or_that does not become this<i>or</i>that

link_patterns = [
    # Match a wiki page link LikeThis.
    (re.compile(r"(\b[A-Z][a-z]+[A-Z]\w+\b)"), r"/\1")
    ]

markdown_renderer = pystache.Renderer()

def new_markdown_handler(filename, context):
    # So we don't pollute our mutable friend:
    my_context = context.copy()

    # TODO - try/finally etc.
    with open(filename,'r') as f:
        m = markdown2.markdown(f.read(), extras=['metadata'], link_patterns=link_patterns)

    # These before metadata, so they're overridable.
    my_context['body'] = unicode(m)
    my_context['_original_filename'] = filename

    # Load metadata - this is messy to cope with [items,with,lists]
    for key,val in m.metadata.iteritems():
        my_context[key] = \
                [{'item':x.strip()} for x in val[1:-1].split(',')] \
            if val[0] == '[' else val

    with open(context['_output_basename'] + '.html','w') as f:
        f.write(pystache.render(my_context['template'], 
                                my_context, 
                                search_dirs=my_context['_template_dir']))

