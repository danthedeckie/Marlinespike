""" handlers.py 
     (C) Copyright 2012 Daniel Fairhead

    This file is part of Marlinespike.

    Marlinespike is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Marlinspike is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Marlinespike.  If not, see <http://www.gnu.org/licenses/>.

"""



import os.path
import re
import pystache
import markdown2
import shutil
import subprocess # for external commands.
from useful import *

def echo_filename(filename, context):
    print os.path.join(context['_output_dir'], filename)

def copy_file(filename, context):
    # TODO - cacheing / checking last date.
    outputfile = os.path.join(context['_output_dir'], filename)
    if not os.path.isfile(outputfile):
        shutil.copy2(filename, outputfile)

def less_handler(filename, context):
    with open(context['_output_basename'] + '.css','w') as f:
        subprocess.call(['lessc', filename], stdout=f)


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
    filename = os.path.join(context['_template_dir'], name + context['_template_extn'])

    if filename in _markdown_templates:
        return _markdown_templates[filename]
    else:
        if os.path.isfile(filename):
            new_template, template_metadata = readfile_with_jsonheader(filename)

            if 'template' in template_metadata:
                replace_string = template_metadata.get('template_replace','{{{ body }}}')
                parent_template = _get_template(template_metadata['template'],context)
                new_template = parent_template.replace(replace_string, new_template)
            _markdown_templates[filename] = new_template 
            return new_template
        else:
            raise RuntimeError('template "' + filename + '" not found.')

_markdown_tag_plugins = {}

__inside_tag_regex = re.compile("\s(?P<key>\S*)\s*=\s*[\"'](?P<val>[^\"']+)")

def register_markdown_tag_plugin(tag, func):
    def make_tag_regex(tag):
        return re.compile("<%\s*"+tag+"(.*?)%>")

    def make_tag_func(func):
        return lambda x: func(**{k:v for k,v in 
            re.findall(__inside_tag_regex, x.groups()[0].__str__())}) 

    _markdown_tag_plugins[tag] = (make_tag_regex(tag), make_tag_func(func))

def _do_markdown_tag_plugins(text):

    def do_tag(partial_text, plugin):
        return re.sub(plugin[0], plugin[1], partial_text)

    return reduce(do_tag, _markdown_tag_plugins.values(), text)


def markdown_handler(filename, context):

    # TODO - try/finally etc.
    text, metadata = readfile_with_jsonheader(filename)
    
    # So we don't polute our mutable friend:
    my_context = dict(context.items() + metadata.items())

    m = markdown2.markdown(_do_markdown_tag_plugins(text), extras=['metadata'], link_patterns=link_patterns)

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

