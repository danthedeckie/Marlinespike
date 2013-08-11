# Marlinespike

A (Work in Progress) reasonably simple and increasingly powerful static website generator.

## Why the name?

Marlinespike is the art of ropework and general seaworthiness of sailors,
named after the tool called a marlinespike, which essentially is a long pointy
stick which is used to seporate strands of rope, give extra purchase or grip
while hauling on some line or other, fighting off pirates, and generally
anything else which you can think of for it.

## Why bother?

I have been using Jekyll - but I don't much like ruby, and prefer to keep
all our projects Python rather than bring yet another language in to it.

Also, it's kinda fun.

Jekyll seems (to me) to be quite a bit complex beast, wheras I think this
ought to be a reasonably simple project.  Almost everything already exists as
libraries.

Writing a new plugin for Jekyll to simply throw .less files at lessc ended up being
20 or so lines of boilerplate, subclassing stuff and generally was a bit of a pain.

I want plugins to be *incredibly* simple to write.  There should be as little
boilerplate as possible. Preferably none.

## Status:

Basics are working, OMNIvision's site is working with this now,
still a lot of cleaning up and polishing needed before 'production ready'.

_WARNING_: The plugin system is still *very much* in progress, and so may not
won't work as expected.

## Getting Started:

    ./setup.sh

Should be enough for most people, and then you can call the *run.sh* script from the folder
you want to use as your website source directory.  The setup.sh script will prompt you on
how to install it if you want to.  Once marlinespike is considered production ready and
stable, I will make a proper installer.

You will normally want to run marlinespike from different places around your computer (from your website source directory).  Either call run.sh from there, or you can create a symlink:

    ln -s /home/daniel/src/Marlinespike/run.sh /usr/local/bin/marlinespike

or whatever.  When you run setup.sh, it will tell you the correct command.

## What does the setup.sh script do?

setup.sh downloads and configures a virtualenv (Python virtual environment) for marlinespike,
and will download all the required modules and put all this in a .virtualenv folder in
the project directory.

The virtualenv is kept in .virtualenv, and you shouldn't have to worry about it.
You don't need to 'enter' or 'exit' the virtualenv.

## Requirements:

As long as you have a working Python(2.7+) installation, the *setup.sh* script should
get you up and running quickly.

Python Modules (listed also in requirements.txt):

- jinja2 (fast, powerful templating system)
- markdown2 (markdown text -> html processing)
- pyscss (SCSS -> CSS)
- PyYAML (YAML frontmatter (a la jekyll/github)

Other non-python requirements (for plugins)

- image-magick (if you want to use the image_magick plugin)
- java (for the yuic javascript compressor, and the htmlcompressor plugins)

## Contact:

Either danthedeckie on github, or www.omnivision.om.org
