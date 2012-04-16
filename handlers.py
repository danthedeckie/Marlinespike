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

