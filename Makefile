TC_PATH = $(dir $(realpath $(firstword $(MAKEFILE_LIST))))

typocheck:
	git ls-files | python $(TC_PATH)/corrector.py

typocheckDir:
	git ls-files | python $(TC_PATH)/corrector.py -d .

# data/extra_endings.txt:
# 	python add_extra_endings.py

data/levenshtein_util_typos.txt:
	# This should be created/updated by typochecker/levenshtein_corrector.py
	touch $@

data/extra_endings.txt: data/levenshtein_util_typos.txt
	cat data/levenshtein_util_typos.txt >> $@
	sort $@ | uniq > data/s.txt
	mv data/s.txt $@

data/wikipedia_common_misspellings_raw.txt:
	echo 'Copy from https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines'

data/wikipedia_common_misspellings.txt: data/wikipedia_common_misspellings_raw.txt
	# Remove noisy typos
	cat data/wikipedia_common_misspellings_raw.txt | grep -v '^aka' | grep -v '^cmo' | grep -v '^significand' > $@
