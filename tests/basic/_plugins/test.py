def test_markdown_plugin(**kwargs):
    kwargs['context'] = "(the context object. lots of stuff in there...)"
    return "Plugin recieved:<ul><li>" + '</li><li>'.join(
        [str(k)+':'+str(v) for k,v in kwargs.items()])+'</li></ul>'

_tag_plugins = {'test': test_markdown_plugin}

