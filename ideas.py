import re

longer_text= \
"""<html> 
blah blah blah 
<% omnitube url="video.html" size="600" %> and then
some more <% omnitube url="here.html" size="900" %></html>"""

text="<% omnitube url='blah.html' width='600' %>"

def make_tag_regex(tag):
    tag_contents_regex = re.compile("<%\s*"+tag+"(.*)%>")

inside_tag_regex = re.compile("\s(?P<key>\S*)=[\"'](?P<val>[^\"']+)")
re.findall(inside_tag_regex,text)

