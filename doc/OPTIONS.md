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
