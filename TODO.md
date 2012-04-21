## Known bugs
(aka unexpected behavior)

- in plugins, <% tagname key="value'subvalue'" %>
  has problems. Regex is wrong, so it ends value at the single
  quote rather than continuing to the double... There is no
  escaping either.  Not good.  Also, multi-line tags should be
  possible.

## Current projects

- figuring out plugin hooks & best practices
  + move "sections" support to a plugin?
- error handling and catching
- documentation

## Next

- caching / mtime & dependancies
- tags / categories, etc.
- blog "year/date/title" type of stuff
- auto-run on changes
- jslint on json fail (part of error handling?)
- yuic javascript/css minifier plugin

## Would be nice

- GUI (osx, windows) / + .app distributable
- profiling, speeding up stuff
- django templates option
- post processing html minifer?
