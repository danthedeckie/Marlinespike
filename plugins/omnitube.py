""" OMNItube plugin:

    Very simple plugin for embedding omnitube.org videos on pages.
    Included in the marlinespike distribution as an example.

"""

def omnitube_tag(video='', height='338', width='600', **kwargs):
    return '<div class="video-container"><iframe type="text/html"  width="' + width + '"' \
           ' height="' + height + '" autoplay="false"' \
           ' src="http://www.omnitube.org/embed.php?video=' + video + ' "' \
           ' frameborder="0"></iframe></div>'

_tag_plugins = {'OMNItube': omnitube_tag}
