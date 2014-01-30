# Plugin hooks:

This is very preliminary documentation.  Sorry it is still pretty rough and in progress.

When writing a plugin, to actually tie stuff into the system, you define lists
in your plugin file.

_context = {'site_name': 'foo'}

for instance.  Will update the context site_name, as you guessed.

Here is a list of currently accepted hooks:

- *_context*
  (as above)
- *_file_handlers* = {'.extn': extn_handler()}
  for handling file types.
  check the plugins scss.py or yuic.py for details of how it actually looks.
- *_tag_plugins* = {'tag_name': tag_func}
  for `<plugin name="blah" options="here" \>` type tags in your markdown files.
- *_post_plugins* = { 'plugin_name': func}
  which get run after processing the markdown file, but before writing it to disk.
  it will only happen *if* you also turn it on for that file (or for a bunch of files
  in a directory), using the context['_post_plugins'] option.


# Future plugin hooks to add:

These are just thoughts, still.

- _dir_handler ??? different name?
  which returns a list of files to process as normal (in that directory)
  of course it can monkey with the dir context in the process.  With these
  plugins, you could filter out certain file types, process files yourself
  in a different way, run custom scripts, change the output directory to
  somewhere totally different (say a 'static' dir? which seems odd since
  marlinespike is for making static sites, but hey.  Perhaps for generating
  cgi-bin perl scripts  and putting them in cgi-bin rather than in the public
  folder...). etc.
- _on_load ?  As soon as the plugin gets loaded, it gets a change to monkey
  with the context?
- _end_of_dir ?
- _end_of_marlinespike_run (end of voyage?)
  possibly also a way to get called if somehow it fails, so on a daily-update or whatever
  if there is a problem, a script/plugin could email an SOS...
- _on_deploy (for minifying scripts, etc)
- _pre_file?
