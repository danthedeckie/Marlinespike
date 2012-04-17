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

def old_markdown_handler(filename, context):
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

_markdown_renderer = pystache.Renderer()
_markdown_templates = {}


def _get_template(name, context):
    if name in _markdown_templates:
        return _markdown_templates[name]
    else:
        # if exists?! TODO
        if True:
            # TODO - some kind of minify metadata? or alternate option for {{{body}}} in template?
            with open(os.path.join(context['_template_dir'],name + context['_template_extn'])) as f:
                new_template = markdown2.markdown(f.read(), extras=['metadata'])

            if 'template' in new_template.metadata:
                replace_string = new_template.metadata['template_replace'] \
                        if 'template_replace' in new_template.metadata \
                        else '{{{body}}}'
                parent_template = _get_template(new_template.metadata['template'],context)
                new_template = parent_template.replace(replace_string, new_template)
            _markdown_templates[name] = new_template # TODO? strip metadata?
            return new_template
        else:
            # Dunno if this is a good idea...
            return '{{{body}}}'


def markdown_handler(filename, context):
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
        f.write(pystache.render(_get_template(my_context['template'], my_context), my_context ))

