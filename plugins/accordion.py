"""  Accordion Plugin:

    This very simple plugin takes text:

        <% accordion text="Hello World" %>

    and returns it as an "a" tag with the "acchead" class.

        <a class="acchead" href="#">Hello World</a>

    This means that with this javascript (w/ jQuery):

        function do_accordions() {
            $('a.acchead').click(function(e) {
                $(this).siblings('ul').slideToggle('fast');
                e.preventDefault();
            }).siblings('ul').hide();
        }

    The following markdown becomes a cool accordion:

        - <% accordion text="More info" %>
          + Item 1
          + Item 2
          + And so on.
        - <% accordion text="Second accordion" %>
          + Here's the second lot
          + Of items
          + To be displayed

    Which I think is quite cool.  You can see examples of this at
    http://www.omnitube.org/

    """
from marlinespike.hull import markdown_handler


def accordion_tag(text="", **kwargs):
    return "<a class=\"acchead\" href=\"#\">" + text + "</a>"

markdown_handler.register_tag_plugin('accordion',accordion_tag)
