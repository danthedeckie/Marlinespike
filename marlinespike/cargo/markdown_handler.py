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
# For pystache/markdown files:
###########

import os.path
import re
import pystache
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


_markdown_renderer = pystache.Renderer()

# Here the already-loaded templates are cached.  When you '_get_template', it checks
# here first.

_markdown_templates = {}

def _get_template(name, context):

    if name == None:
        # if no template selected, return an empty one (rather than crashing)
        logging.info('Using blank/no template for {0}'.format( context['_output_basename']))
        return '{{{ body }}}'

    inputfile = os.path.join(context['_template_dir'], name + context['_template_extn'])

    if inputfile in _markdown_templates:
        return _markdown_templates[inputfile]
    else:
        if os.path.isfile(inputfile):
            new_template, template_metadata = readfile_with_jsonheader(inputfile)

            if 'template' in template_metadata:
                replace_string = template_metadata.get('template_replace', '{{{ body }}}')
                parent_template = _get_template(template_metadata['template'], context)
                new_template = parent_template.replace(replace_string, \
                                                       new_template)
            _markdown_templates[inputfile] = new_template
            return new_template
        else:
            raise IOError('template "' + inputfile + '" not found.')

_markdown_tag_plugins = {}
_post_markdown_plugins = {}



class markdown(CargoHandler):
    def make_outputfile_name(self, inputfile, context):
        return context['_output_basename'] + '.html'

    def register_post_plugin(self, name, func):
        _post_markdown_plugins[name] = func

    def register_tag_plugin(self, tag, func):
        """ takes 'tag' and 'function'.  The function will be sent all values
            in a tag as named arguments (useful), but in case you get sent mad
            data, it's usually a good idea for your function to also take the
            catchall *kwargs as well.  """
        def make_tag_regex(tag):
            return re.compile("<%\s*" + tag + "(.*?)%>")

        def parse_plugindata(tag_data):
            """ takes a key='value' type html tag attributes string, and returns a
              dict {key:value} """
            parser = TagPluginParser()
            parser.feed('<PLUGIN ' + tag_data + ' />')
            return parser.attributes

        def make_tag_func(func):
            # This returns an anonymous function which takes a regex-parsed 'groups'
            # (all the <% plugin ...BLAH... %> bits for this plugin) and returns
            # a dict of keys & values within '...BLAH...'
            return lambda x: func(**parse_plugindata(x.groups()[0].__str__()))

        _markdown_tag_plugins[tag] = (make_tag_regex(tag), make_tag_func(func))

    def _do_markdown_tag_plugins(self, text):

        def do_tag(partial_text, (plugin_regex, plugin_func)):
            return re.sub(plugin_regex, plugin_func, partial_text)

        return reduce(do_tag, _markdown_tag_plugins.values(), text)


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
        text, metadata = readfile_with_jsonheader(inputfile)

        # So we don't polute our mutable friend:
        my_context = dict(context.items() + metadata.items())

        m = markdown2.markdown(self._do_markdown_tag_plugins(text), \
                               extras=['metadata'], link_patterns=link_patterns)

        # These before metadata, so they're overridable.
        my_context['body'] = unicode(m)
        my_context['_original_inputfile'] = inputfile

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
            f.write(pystache.render(_get_template(my_context.get('template', None), my_context), \
                                    my_context))
