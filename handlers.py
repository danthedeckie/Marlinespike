import pystache
import markdown2

def echo_filename(filename, context):
    print 'ECHO!:'
    print filename

def mustache_handler(filename, context):
    print 'MUSTACHE!:'
    print filename

def markdown_handler(filename, context):
    print 'Markdown:'
    print filename

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


def markdown_handler(filename, context):
    # So we don't pollute our mutable friend:
    my_context = context.copy()

    # TODO - try/finally etc.
    with open(filename,'r') as f:
        m = markdown2.markdown(f.read(), extras=['metadata'], link_patterns=link_patterns)

    # These before metadata, so they're overridable.
    my_context['body'] = unicode(m)
    my_context['_filename'] = os.path.splitext(os.path.basename(filename))[0]
    my_context['_original_filename'] = filename

    # Load metadata - this is messy to cope with [items,with,lists]
    for key,val in m.metadata.iteritems():
        my_context[key] = \
                [{'item':x.strip()} for x in val[1:-1].split(',')] \
            if val[0] == '[' else val

    with open(os.path.join(my_context['output_dir'], my_context['_filename'] + '.html'),'w') as f:
        f.write(pystache.render(my_context['template'], my_context, partials=my_context['templates']))


