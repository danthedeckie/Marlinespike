def test_markdown_plugin(**kwargs):
    return "Plugin recieved:<ul><li>" + '</li><li>'.join(
        [str(k)+':'+str(v) for k,v in kwargs.items()])+'</li></ul>'

markdown_handler.register_tag_plugin('test',test_markdown_plugin)


