"""  Accordion Plugin:

    This very simple plugin takes text:

        <plugin name="accordion" text="Hello World" \>

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

        - <plugin name="accordion" text="More info" \>
          + Item 1
          + Item 2
          + And so on.
        - <plugin name="accordion" text="Second accordion" \>
          + Here's the second lot
          + Of items
          + To be displayed

    Which I think is pretty sweet, for such minimal markup.
    You can see examples of this at http://omnivision.om.org/

    """

def accordion_tag(text="", **kwargs):
    return "<a class=\"acchead\" href=\"#\">" + text + "</a>"

_tag_plugins = {'accordion': accordion_tag}
