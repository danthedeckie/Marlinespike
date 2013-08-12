"""  markdown_handler.py -- Marlinespike Markdown Cargo Handler
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



###########
# For jinja2/markdown files:
###########

import os.path
import re
from jinja2 import Template, FileSystemLoader, Environment
import markdown2
from HTMLParser import HTMLParser

from marlinespike.cargo import CargoHandler
from marlinespike.useful import *

# from tests.

#TAB_LENGTH = 4            # expand tabs to this many spaces
ENABLE_ATTRIBUTES = True  # @id = xyz -> <... id="xyz">
SMART_EMPHASIS = 1        # this_or_that does not become this<i>or</i>that

link_patterns = [
    # Match a wiki page link LikeThis.
    (re.compile(r"(\b[A-Z][a-z]+[A-Z]\w+\b)"), r"/\1")
    ]

########
# Epicly simple markdown 'plugin' system parser (hurrah for python batteries included)
########

class TagPluginParser(HTMLParser):
    def __init__(self):
        self.attributes = {}
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        # is there a better way to do this?
        # NOTE: this is python2.7 only!
        self.attributes = {k:v for k,v in attrs}


# Here the already-loaded templates are cached.  When you '_get_template', it checks
# here first.

_markdown_templates = {}

def _get_template(name, context):

    if name == None:
        # if no template selected, return an empty one (rather than crashing)
        logging.info('Using blank/no template for {0}'.format( context['_output_basename']))
        return '{{ body }}'

    inputfile = os.path.join(context['_template_dir'], name + context['_template_extn'])

    loader = FileSystemLoader(context['_template_dir'])
    environment = Environment(loader=loader)

    # TODO: caching stuff...
    #cache = FileSystemBytecodeCache(context[

    if inputfile in _markdown_templates:
        return _markdown_templates[inputfile]
    else:
        try:
            new_template = environment.get_template(name + context['_template_extn'])
            _markdown_templates[inputfile] = new_template

            return new_template
        except Exception as e:
            raise e
            raise IOError('template "' + inputfile + '" not found, or invalid.')

_markdown_tag_plugins = []
_post_markdown_plugins = {}

def _make_tag_regex(tag):
    return re.compile("<%\s*" + tag + "(.*?)%>")

class MarkdownTagPlugin(object):
    def __init__(self, tag, function):
        self.handle_function = function
        self.tag = tag
        self.regex = _make_tag_regex(tag)

class markdown(CargoHandler):
    def make_outputfile_name(self, inputfile, context):
        return context['_output_basename'] + '.html'

    def register_post_plugin(self, name, func):
        _post_markdown_plugins[name] = func

    def register_tag_plugin(self, tag, func):
        _markdown_tag_plugins.append(MarkdownTagPlugin(tag, func))

    def _do_markdown_tag_plugins(self, text, context):
        text_in_process = text
        for tag_plugin in _markdown_tag_plugins:
            def process (tag_data):
                # the re.sub function sends us a weird object. we only need
                # the internal text bit:
                tag_internal_text = tag_data.groups()[0].__str__()
                # takes the x="blah" bit of a tag, compiles it to a dict:
                parser = TagPluginParser()
                parser.feed('<PLUGIN ' + tag_internal_text + ' />')
                # adds the context:
                parser.attributes['context'] = context
                # sends it all to the handler:
                try:
                    return tag_plugin.handle_function(**parser.attributes)
                except Exception as e:
                    logging.error('Error with tag plugin! (' + tag_plugin.tag + ')')
                    logging.error(e.message)
                    # TODO - catch and report better.
                    raise e

            text_in_process = re.sub(tag_plugin.regex, process, text_in_process)

        return text_in_process

    def process_file(self, inputfile, context):
        outputfile = self.make_outputfile_name(inputfile, context)

        # TODO - somehow caching / mtime / something for templates
        #        and these files so they only update when needed.
        #
        #        file_newer_than(template, outputfile) and \
        #        file_newer_than(inputfile, outputfile)
        #
        #        although currently the template cache is very basic,
        #        and doesn't contain metadata such as filename, date,
        #        etc.

        logging.info('Updating:' + inputfile)  
        # TODO - try/finally etc.
        text, metadata = readfile_with_json_or_yaml_header(inputfile)

        # So we don't polute our mutable friend:
        my_context = dict(context.items() + metadata.items())

        m = markdown2.markdown(self._do_markdown_tag_plugins(text, my_context), \
                               extras=['metadata'], link_patterns=link_patterns)

        # These before metadata, so they're overridable.
        my_context['body'] = unicode(m)
        my_context['_original_inputfile'] = inputfile

        # Load metadata - this is messy to cope with [items,with,lists]
        # TODO: remove this and recommend JSON metadata?
        for key, val in m.metadata.iteritems():
            if isinstance(val, list):
                my_context[key] = val
            else:
                my_context[key] = \
                        [{'item':x.strip()} for x in val[1:-1].split(',')] \
                    if val.startswith('[') else val

        # Sections:
        # Should this be 'plugin'd out? TODO
        # TODO? default _section?  or defined in _config.json? 
        my_section = my_context.get('section', my_context.get('default_section', None))

        if 'sections' in my_context:
            my_section_dict = filter(lambda x: x.get('title',None) == my_section, my_context['sections'])
            if my_section_dict:
                my_section_dict[0]['current'] = True

        # Run the post_markdown plugins...

        for plugin in my_context.get('plugins',[]):
            if _post_markdown_plugins.has_key(plugin):
                _post_markdown_plugins[plugin](my_context)

        # And write the file:

        with open(outputfile, 'w') as f:
            template = _get_template(my_context.get('template', None), my_context)
            f.write( template.render( my_context))
