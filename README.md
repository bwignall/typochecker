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

## Whitelist words

Not all nominal typos are genuine typos. For example, your domain may use 
terminology that has spelling similar to some non-technical words. To have 
those not flagged as typos, you can specify whitelisted words. These may 
be specified directly on the command invocation, via a file, or both.

Examples, direct:
```shell script
python corrector.py --dir BASE_DIRECTORY -w exampleone
python corrector.py --dir BASE_DIRECTORY -w exampleone -w exampletwo
```

Examples, whitelist file:
```shell script
python corrector.py --dir BASE_DIRECTORY -W fileone
python corrector.py --dir BASE_DIRECTORY -W fileone -W filetwo
```

Examples, mixed:
```shell script
python corrector.py --dir BASE_DIRECTORY -w wordone -W fileone
python corrector.py --dir BASE_DIRECTORY -w wordone -w wordtwo -W fileone
python corrector.py --dir BASE_DIRECTORY -w wordone -W fileone -W filetwo
```

Note that words are listed explicitly via `-w` (i.e., lowercase) and 
files are via `-W` (i.e., uppercase); long-form options exist for both;
add `-h`/`--help` for details. 

# Gotchas

The tool splits on non-alphabetical characters, 
so corrections for words like `doens't` should be fixed with `doesn` 
(the `'t` does not match, and so is not replaced; 
entering `doesn't` would result in `doesn't't` in the resulting text).

# Source of likely typos

The tool uses information from 
[https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines](Wikipedia)
as a source of useful typos to check for. Note that some typos (e.g., "wich") contain multiple potential corrections.
