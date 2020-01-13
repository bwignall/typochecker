import os
import re
from collections import Counter


# <Norvig>
def wordify(text):
    return re.findall(r'\w+', text.lower())


WORDS = Counter(wordify(open('/usr/share/dict/american-english-huge').read()))
WORDS.update(wordify(open('/usr/share/dict/british-english-huge').read()))


def candidates(word):
    """Generate possible spelling corrections for word."""
    # Unlike Norvig's solution, does *NOT* consider distance-2 edits
    # return known([word]) or known(edits1(word)) or known(edits2(word)) or [word]
    return known([word]) or known(edits1(word)) or [word]


def known(words):
    """The subset of `words` that appear in the dictionary of WORDS."""
    return set(w for w in words if w in WORDS)


def edits1(word):
    """All edits that are one edit away from `word`."""
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]

    return set(deletes + inserts + replaces + transposes)
    # return set(replaces + transposes)
    # return set(deletes + inserts + transposes)
    # return set(inserts + transposes)
    # return set(transposes)


def edits2(word):
    """All edits that are two edits away from `word`."""
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


# </Norvig>

def parse_typos_file(loc):
    print('opening {}'.format(loc))
    with open(loc, 'r') as fname:
        ls = fname.readlines()

    d = {}

    for line in ls:
        k, v = line.strip().split('->')
        d.update({k: v})

    return d


def get_visible_subdirs(loc):
    all_files = []
    for root, dirs, files in os.walk(loc):
        if any([d.startswith('.') for d in root.split(os.sep)
                if d != '.']):
            # Ignore hidden directories
            # (which are assumed to start with '.')
            continue
        else:
            all_files.extend([os.path.join(root, filename)
                              for filename in files])

    return all_files


def get_words_in_string(s):
    words = re.findall(r'[\w]+', s)

    return words


def get_words_in_file(f):
    with open(f, 'r') as ff:
        lines = ff.readlines()

    # Ignore lines that have email addresses
    lines = [line.strip().replace('\\n', '') for line in lines if '@' not in line]

    return get_words_in_string(' '.join(lines))


def get_default_typos():
    # By default, use typos gathered at
    # https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines
    typos_loc = os.path.join(os.path.dirname(__file__),
                             os.pardir, 'data', 'wikipedia_common_misspellings.txt')
    extra_typos_loc = os.path.join(os.path.dirname(__file__),
                                   os.pardir, 'data', 'extra_endings.txt')

    typos = parse_typos_file(typos_loc)
    extra_typos = parse_typos_file(extra_typos_loc)

    typos = {**typos, **extra_typos}

    return typos
