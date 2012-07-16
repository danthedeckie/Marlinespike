###########
# For pystache/markdown files:
###########

import os.path
import re
import pystache
import markdown2
from useful import *

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



class markdown(handler):
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

        __inside_tag_regex = re.compile("\s(?P<key>\S*)\s*=\s*[\"'](?P<val>[^\"']+)")
        # TODO: fix
        # ^^^ bug is here.
        # maybe something to do with
        # \"(\\.|[^\"])*\"
        # or some ideas from 
        # http://stackoverflow.com/questions/249791/regex-for-quoted-string-with-escaping-quotes

        def make_tag_func(func):
            # This returns an anonymous function which takes each of the (key,value) pairs 
            # returned from the regex, and turns it into a dict, which it then passes as 
            # named arguments to func.
            return lambda x: func(**{k: v for k, v in
                re.findall(__inside_tag_regex, x.groups()[0].__str__())})

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
            f.write(pystache.render(_get_template(my_context['template'], my_context), \
                                    my_context))
