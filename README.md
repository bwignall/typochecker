A tool to help (semi-)automatically find typos.
By default, uses Wikipedia as source of likely typos.

# Get the code

For now, the code is run via cloning from GitHub
(a PR to make this pip-installable would be welcomed).

```shell script
git clone https://www.github.com/bwignall/typochecker
cd typochecker
```

# Usage:

## Specify the folder explicitly

```shell script 
python -m typochecker.corrector --dir BASE_DIRECTORY
```

Example: `python corrector.py -d path/to/dest/folder` 
(This assumes that `corrector.py` is in your Python path.) 

This will traverse `BASE_DIRECTORY` and its subdirectories.

## Let Git find files
```shell script 
make -f path/to/typochecker/Makefile
```

Example (explicit): `cd path/to/my/folder ; git ls-files | python path/to/my/git/src/typochecker/corrector.py`

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
python -m typochecker.corrector --dir BASE_DIRECTORY -w exampleone
python -m typochecker.corrector --dir BASE_DIRECTORY -w exampleone -w exampletwo
```

Examples, whitelist file:
```shell script
python -m typochecker.corrector --dir BASE_DIRECTORY -W fileone
python -m typochecker.corrector --dir BASE_DIRECTORY -W fileone -W filetwo
```

Examples, mixed:
```shell script
python -m typochecker.corrector --dir BASE_DIRECTORY -w wordone -W fileone
python -m typochecker.corrector --dir BASE_DIRECTORY -w wordone -w wordtwo -W fileone
python -m typochecker.corrector --dir BASE_DIRECTORY -w wordone -W fileone -W filetwo
```

Note that words are listed explicitly via `-w` (i.e., lowercase) and 
files are via `-W` (i.e., uppercase); long-form options exist for both;
add `-h`/`--help` for details. 

# Gotchas

The tool splits on non-alphabetical characters, 
so corrections for words like `doens't` should be fixed with `doesn` 
(the `'t` does not match, and so is not replaced; 
entering `doesn't` would result in `doesn't't` in the resulting text).

# Custom typos: using your own codebase as a corpus

The original list of typos was based on a general-purpose list from 
Wikipedia. The typochecker codebase contains another list of typos, 
based on scanning some large and well-used codebases. But if you have 
a different work or codebase, it may not be well represented by the data 
used in generating these lists. You may apply a provided script for 
applying heuristics to sniff out possible typos in your work.

```shell script
# Minimal invocation:
python -m typochecker.levenshtein_corrector BASE_DIRECTORY

# Invocation to remove often-unhelpful suggestions
python -m typochecker.levenshtein_corrector --ignore-appends --ignore-prepends BASE_DIRECTORY
```

This will generate a file, which then needs to be folded into
a list of typos known to the program:

```shell script
make data/extra_endings.txt 
```

The `corrector` script may then be run as usual, as described above.

# Source of likely typos

The tool uses information from 
[Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines)
as a source of useful typos to check for. Note that some typos (e.g., "wich") contain multiple potential corrections.
