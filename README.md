A tool to help (semi-)automatically find typos.
By default, uses Wikipedia as source of likely typos.

# Usage:

## Specify the folder explicitly

```shell script 
python corrector.py --dir BASE_DIRECTORY
```

Example: `python corrector.py -d path/to/dest/folder` 
(This assumes that `corrector.py` is in your Python path.) 

This will traverse `BASE_DIRECTORY` and its subdirectories.

## Let Git find files
```shell script 
make -f path/to/typochecker/Makefile
```

Example (explicit): `cd path/to/my/folder ; git ls-files | python path/to/my/git/src/corrector.py`

For either method, this will iterate through the files found, cross-reference the 
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
