TC_PATH = $(dir $(realpath $(firstword $(MAKEFILE_LIST))))

typocheck: 
	git ls-files | python $(TC_PATH)/corrector.py

data/wikipedia_common_misspellings_raw.txt:
	echo 'Copy from https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines'

data/wikipedia_common_misspellings.txt: data/wikipedia_common_misspellings_raw.txt
	# Remove noisy typos
	cat data/wikipedia_common_misspellings_raw.txt | grep -v '^aka' | grep -v '^cmo' > $@
