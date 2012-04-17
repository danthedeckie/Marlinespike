import os.path
import re
import pystache
import markdown2
import shutil
from useful import *

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
        if os.path.isfile(os.path.join(context['_template_dir'], name + context['_template_extn'])):
            new_template, template_metadata = readfile_with_jsonheader( \
                    os.path.join(context['_template_dir'], \
                    name + context['_template_extn']))

            if 'template' in template_metadata:
                replace_string = template_metadata.get('template_replace','{{{ body }}}')
                parent_template = _get_template(template_metadata['template'],context)
                new_template = parent_template.replace(replace_string, new_template)
            _markdown_templates[name] = new_template 
            return new_template
        else:
            raise RuntimeError('template "' + name + '" not found.')


def markdown_handler(filename, context):

    # TODO - try/finally etc.
    text, metadata = readfile_with_jsonheader(filename)
    
    # So we don't polute our mutable friend:
    my_context = dict(context.items() + metadata.items())

    m = markdown2.markdown(text, extras=['metadata'], link_patterns=link_patterns)

    # These before metadata, so they're overridable.
    my_context['body'] = unicode(m)
    my_context['_original_filename'] = filename

    # Load metadata - this is messy to cope with [items,with,lists]
    # TODO: remove this and recommend JSON metadata?
    for key,val in m.metadata.iteritems():
        my_context[key] = \
                [{'item':x.strip()} for x in val[1:-1].split(',')] \
            if val[0] == '[' else val

    with open(context['_output_basename'] + '.html','w') as f:
        f.write(pystache.render(_get_template(my_context['template'], my_context), my_context ))

