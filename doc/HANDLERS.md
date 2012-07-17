## Handlers, and how they work:
---

To keep the sea-faring metaphor going a little longer, file-handlers are called
cargo-handlers in marlinespike.  WHY!?!? you may ask, well, firstly it keeps
the name a little less generic and vague, and secondly, I think it is a little
cooler.

---


A handler is a simple plugin to marlinespike which 'handles' an input file.

The most normal kind of handler is one which throws the input file at an external
program, and puts the result into a similarly named file in the output directory.

the plugins/less.py file is an example of this.

also in handlers.py are a couple of standard ones.

Here is the "pngcrush" compressor for javascript files:

```python
class pngcrush(external_handler):
   command = 'pngcrush'
   fallback = copy_file

   def run(self, inputfile, outputfile, context):
      external_hide_output(self.command, inputfile, outputfile)
```

which is fairly simple.  here is the rundown:

*command* is the program you want to use.  marlinespike will first check to see if it can find it,
  if not, then it will fall back to the fallback handler. (if you don't define a fallback, then
  when marlinespike encounters a file that needs this handler, it will fail with an error explaining
  the situation).  In our example, yuic is merely compressing the data, so if it can't find it,
  it will just copy the original file instead.  You do need to define a command, however.

*run* is a method which you need to define. It is what will actually get called.
  external_print_output(...) runs the command you specify, with arguments.  you don't need to quote
  filenames, or any of that.  it takes care of it.  There are also functions:
  external_hide_output(...) - for noisy programs (hides their output)
  external_use_output(output_file, ...) which takes a first argument of the filename to 
  output to, and then then as normal.

You can also define a method:

```python
   def make_outputfile_name(self, filename, context):
       return context['_output_basename'] + '.css'
```

You can return whatever filename you like.  If you don't define a *make_outputfile_name* method,
then it will default to the same filename as the original file (although, it'll be in the output directory...)

## Non-normal or non-external handlers

If you don't want all the clobber normally needed with an external handlers (say you 
want to write something funky in python) then you don't need to inherit from the 
*external_handler* class.  for instance, here's the copy_file handler:

```python
class hardlink_file(cargo_handler):
    def run(self, inputfile, outputfile, context):
        os.link(inputfile, outputfile)
```

looks pretty similar.  

TODO: include diagram of how handlers work, process_file (calls run), etc, show example of 
doing really wacky stuff, etc.

