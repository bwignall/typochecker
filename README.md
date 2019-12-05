A tool to help (semi-)automatically find typos in Git repositories. 
By default, uses Wikipedia as source of likely typos.

# Usage:

```shell script 
make -f path/to/typochecker/Makefile
```

This will iterate through the files Git knows, cross-reference the 
list of likely typos, and prompt the user for how they would like to handle
each potential typo. Files will be modified, but no Git commits happen 
automatically.

* To accept the suggestion, press Enter.
* To ignore the suggestion and keep the existing text, enter `!` or `/`.
(`Ctrl-D` may also work.)
* For help, enter `!h`.

# Gotchas

The tool splits on non-alphabetical characters, 
so corrections for words like `doens't` should be fixed with `doesn` 
(the `'t` does not match, and so is not replaced; 
entering `doesn't` would result in `doesn't't` in the resulting text).

# Source of likely typos

The tool uses information from 
[https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines](Wikipedia)
as a source of useful typos to check for. Note that some typos (e.g., "wich") contain multiple potential corrections.