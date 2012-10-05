# Marlinespike

A very simple _(but hopefully soon powerful)_ static site generator.

## Why the name?

Marlinespike is the art of ropework and general seaworthiness of sailors, 
named after the tool called a marlinespike, which essentially is a long pointy
stick which is used to seporate strands of rope, give extra purchase or grip
while hauling on some line or other, fighting off pirates, and generally 
anything else which you can think of for it.

## Why bother?

I have been using Jekyll - but I don't much like ruby, and prefer to keep
all our projects python rather than bring yet another language in to it.

Also, it's fun.

Also, Jekyll seems (to me) to be quite a bit complex beast, wheras I think this
ought to be a reasonably simple project.  Almost everything already exists as
libraries.

Writing a new plugin for Jekyll to simply throw .less files at lessc ended up being
20 or so lines of boilerplate, subclassing stuff and generally was a bit of a pain.

I want plugins to be *incredibly* simple to write.  There should be as little 
boilerplate as possible. Preferably none.

## Status:

Basics are working, our next generation site is working with this now,
still a lot of cleaning up and polishing needed before 'production ready'.
_WARNING_: The plugin system is still *very much* in progress, and so probably
won't work as expected.

## Requirements:

- Python>=2.7.  I'm working here with 2.7.3
- pystache (for templating) (easy_install pystache)
- markdown2 (for markdown files) (easy_install markdown2)
- lessc (if you want to use the less to css plugin)
- pyscss (if you want to use the scss plugin)
- yuic (if you want to use the javascript/css minifier plugin)
- image-magick (if you want to use the image_magick plugin)

## Contact:

Either danthedeckie on github, or www.omnivision.om.org
