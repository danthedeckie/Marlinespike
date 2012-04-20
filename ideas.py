import re

text="<% omnitube url='blah.html' width='600' %>"
re.findall("\s(?P<key>\S*)=[\"'](?P<val>[^\"']+)",text)

