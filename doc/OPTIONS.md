# Options for configuration

configuation details are normally kept in "_config.json"
each directory can override / add to previous (parent) settings with their own "_config.json" file.

## _config.json values:

- ### "_output_dir"
  where you want files from this directory to go.  defaults to the parent's directory +
  the current directory name

- ### "_template_dir"
  where templates(usually .md) can be found.  I recommend that you use one _template_dir
  for the whole site, and then reference templates

- ### "_base_path"
  a relative link to the root directory of the project. (so in a subdirectory, it will
  be '../' in the root directory it'll be blank, and so on.


## blog plugin values:

These are used by the blog plugin.

- ### "_blog_date_format"
  what format you want the dates to end up in.
  this format can be found in (python documentation)[http://docs.python.org/library/time.html?highlight=time#time.strftime] (%Y-%m-%d kind of thing)

- ### "_blog_filedate_format"
  what format to read dates from the beginning of filenames in.
  same deal for formatting as _blog_date_format.

- ### "_blog_more_text"
  you can trim how much of blogposts are displayed in a list (not on it's main page)
  by putting <% more %>.  Usually that's replaced as a ... 'read more' or similar.
  this lets you choose what text to have.
  NOTE: you need to do this *yourself* in the blog listing template file. ;-)

- ### "_blog_more_class"
  to make life easier, the text displayed as _blog_more_text is wrapped for you in
  an <a>_a_</a> tag (a link). It will be given this class, so you can theme it as
  you see fit (or hide it altogether) with CSS.
