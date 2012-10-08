## Multi-lingual plugin:

One problem I had with a website I helped with once (running
in an 'easy' point and click interface) was in order to get
multi-lingual stuff working sensibly, massive ammounts of
javascript hackery were needed. (overrides, custom scripts, etc)
In theory, it should NOT be a hard problem to solve.  This is my
thoughts for how the multi-lingual plugin should work in marlinespike.

### Directory structure looks like:

- /en/
  - index.markdown
  - help.markdown
  - contact.markdown

- /de/
  - index.markdown
  - hilfe.markdown
  - kontakt.markdown

- /el/
  - index.markdown

- /es/
  - redirect-to-spanish-google.markdown

### Config says:

- use the multi-lingual plugin.
- the 'original' dir is 'en'
- translation dirs are ['de', 'el', 'es']

### On entering any translation dir:
(Note: there is no plugin hook for this yet...)

```python
    for all files in original_dir but not here:
        load file from original_dir
        update file.context with context from this dir
        # which gives us any local site name translation
        # strings, and correct output directory.
        write the file as normal (into this translations output dir)
        tell log file 'no translation available for $file, so using original in $dir'
```


### On entering any file in a translation dir:
```python
    # So we can have de/hilfe and de/kontakt rather than de/help and de/contact...
    counterpart = context.get('counterpart', filename)

    if counterpart_exists in original_dir:
        with load_file(counterpart) as file:
            update file.context with context from current translation file
            file.output() # as normal
```

