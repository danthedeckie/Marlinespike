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
import subprocess  # for external commands.
from useful import *
import logging

def echo_filename(filename, context):
    print os.path.join(context['_output_dir'], filename)


# it should be fairly obvious that a lot of the following is
# boilerplate, and can probably be abstracted out. TODO.

def copy_file(filename, context):
    outputfile = os.path.join(context['_output_dir'], filename)
    if not file_already_done(filename, outputfile):
        logging.info("Updating:" + filename)
        shutil.copy2(filename, outputfile)


def less_handler(filename, context):
    need_shell_command('lessc')

    outputfile = context['_output_basename'] + '.css'
    if not file_already_done(filename, outputfile):
        logging.info("Updating:" + filename)
        with open(outputfile, 'w') as f:
            subprocess.call(['lessc', filename], stdout=f)


def pngcrush_handler(filename, context):
    if not shell_command_exists('pngcrush'):
        logging.info('pngcrush not found. copying instead')
        return copy_file(filename, context)

    outputfile = context['_output_basename'] + '.png'
    if not file_already_done(filename, outputfile):
        logging.info("PNGCrush:" + filename)
        subprocess.call (['pngcrush', filename, outputfile]) 


def yuic_js_handler(filename, context):
    if not shell_command_exists('yuic'):
        logging.info('yuic not found. copying instead')
        return copy_file(filename, context)

    outputfile = context['_output_basename'] + '.js'
    if not file_already_done(filename, outputfile):
        logging.info("YUIC:" + filename)
        subprocess.call(['yuic', filename, '-o', outputfile])

###########
# For pystache/markdown files:
# This is long and complex enough to warrant it's own file very soon.
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

# Here the already-loaded templates are cached.  When you '_get_template', it checks
# here first.

_markdown_templates = {}

def _get_template(name, context):
    filename = os.path.join(context['_template_dir'], name + context['_template_extn'])

    if filename in _markdown_templates:
        return _markdown_templates[filename]
    else:
        if os.path.isfile(filename):
            new_template, template_metadata = readfile_with_jsonheader(filename)

            if 'template' in template_metadata:
                replace_string = template_metadata.get('template_replace', '{{{ body }}}')
                parent_template = _get_template(template_metadata['template'], context)
                new_template = parent_template.replace(replace_string, \
                                                       new_template)
            _markdown_templates[filename] = new_template
            return new_template
        else:
            raise RuntimeError('template "' + filename + '" not found.')

_markdown_tag_plugins = {}
_post_markdown_plugins = {}

__inside_tag_regex = re.compile("\s(?P<key>\S*)\s*=\s*[\"'](?P<val>[^\"']+)")

def register_post_markdown_plugin(name, func):
    _post_markdown_plugins[name] = func

def register_markdown_tag_plugin(tag, func):
    """ takes 'tag' and 'function'.  The function will be sent all values
        in a tag as named arguments (useful), but in case you get sent mad
        data, it's usually a good idea for your function to also take the
        catchall *kwargs as well.  """
    def make_tag_regex(tag):
        return re.compile("<%\s*" + tag + "(.*?)%>")

    def make_tag_func(func):
        # This returns an anonymous function which takes each of the (key,value) pairs 
        # returned from the regex, and turns it into a dict, which it then passes as 
        # named arguments to func.
        return lambda x: func(**{k: v for k, v in
            re.findall(__inside_tag_regex, x.groups()[0].__str__())})

    _markdown_tag_plugins[tag] = (make_tag_regex(tag), make_tag_func(func))


def _do_markdown_tag_plugins(text):

    def do_tag(partial_text, (plugin_regex, plugin_func)):
        return re.sub(plugin_regex, plugin_func, partial_text)

    return reduce(do_tag, _markdown_tag_plugins.values(), text)


def markdown_handler(filename, context):
    # TODO - somehow caching / mtime / something for templates
    #        and these files so they only update when needed.
    logging.info('Updating:' + filename)  
    # TODO - try/finally etc.
    text, metadata = readfile_with_jsonheader(filename)

    # So we don't polute our mutable friend:
    my_context = dict(context.items() + metadata.items())

    


    m = markdown2.markdown(_do_markdown_tag_plugins(text), \
                           extras=['metadata'], link_patterns=link_patterns)

    # These before metadata, so they're overridable.
    my_context['body'] = unicode(m)
    my_context['_original_filename'] = filename

    # Load metadata - this is messy to cope with [items,with,lists]
    # TODO: remove this and recommend JSON metadata?
    for key, val in m.metadata.iteritems():
        my_context[key] = \
                [{'item':x.strip()} for x in val[1:-1].split(',')] \
            if val.startswith('[') else val

    # Sections:
    # Should this be 'plugin'd out? TODO
    # TODO? default _section?  or defined in _config.json? 
    my_section = my_context.get('section', my_context.get('default_section', None))

    if "sections" in my_context:
        my_section_dict = filter(lambda x: x.get('title',None) == my_section, my_context['sections'])
        if my_section_dict:
            my_section_dict[0]['current'] = True

    # Run the post_markdown plugins...

    for plugin in my_context.get('plugins',[]):
        if _post_markdown_plugins.has_key(plugin):
            _post_markdown_plugins[plugin](my_context)

    # And write the file:

    with open(context['_output_basename'] + '.html', 'w') as f:
        f.write(pystache.render(_get_template(my_context['template'], my_context), \
                                my_context))
