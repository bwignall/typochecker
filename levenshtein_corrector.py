# Use heuristics inspired by Peter's Norvig's spelling corrector,
# https://norvig.com/spell-correct.html
# https://github.com/norvig/pytudes/blob/master/py/spell.py

import argparse
import os
import re
from collections import Counter

# Assumption: long lines (e.g., in JSON files) should be skipped
MAX_LINE_LEN = 200


# <Norvig>
def words(text): return re.findall(r'\w+', text.lower())


WORDS = Counter(words(open('/usr/share/dict/american-english-huge').read()))
WORDS.update(words(open('/usr/share/dict/british-english-huge').read()))


def P(word, N=sum(WORDS.values())):
    """Probability of `word`."""
    return WORDS[word] / N


def correction(word):
    """Most probable spelling correction for word."""
    return max(candidates(word), key=P)


def candidates(word):
    """Generate possible spelling corrections for word."""
    # Unlike Norvig's solution, does *NOT* consider distance-2 edits
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])
    # return known([word]) or known(edits1(word)) or [word]


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
    # return set(deletes + transposes + replaces + inserts)
    # return set(transposes + replaces)
    # return set(transposes + inserts + deletes)
    return set(transposes + inserts)
    # return set(transposes)


def edits2(word):
    """All edits that are two edits away from `word`."""
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


# </Norvig>

def get_words_in_string(s):
    words = re.findall(r'[\w]+', s)

    return words


def get_words_in_file(f):
    with open(f, 'r') as ff:
        lines = ff.readlines()

    # Ignore lines that have email addresses
    lines = [l.strip().replace('\\n', '') for l in lines if '@' not in l]

    return get_words_in_string(' '.join(lines))


def get_typos(loc):
    print('opening {}'.format(loc))
    with open(loc, 'r') as fname:
        ls = fname.readlines()

    d = {}

    for line in ls:
        k, v = line.strip().split('->')
        d.update({k: v})

    return d


def is_new_typo(suspected_typo):
    typo, correction = suspected_typo
    try:
        response_raw = input('{}->{} ("!" to accept, "" to ignore): '.format(typo, correction))
        if response_raw.startswith('!'):
            return suspected_typo
        elif len(response_raw) > 1:
            return typo, response_raw
        else:
            return None
    except:
        return None


def get_known_words(loc='/usr/share/dict/american-english'):
    return set([w.lower() for w in get_words_in_file(loc)])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Search this directory, recursively, to find files to check')
    parser.add_argument('--ignore-prepends', action='store_true',
                        help='If set, ignore suggestions where characters are only added to the front')
    parser.add_argument('--ignore-appends', action='store_true',
                        help='If set, ignore suggestions where characters are only added to the end')

    args = parser.parse_args()

    # By default, use typos gathered at
    # https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines
    TYPOS_LOC = os.path.join(os.path.dirname(__file__),
                             'data', 'wikipedia_common_misspellings.txt')
    EXTRA_TYPOS_LOC = os.path.join(os.path.dirname(__file__),
                                   'data', 'extra_endings.txt')

    typos = get_typos(TYPOS_LOC)
    extra_typos = get_typos(EXTRA_TYPOS_LOC)

    typos = {**typos, **extra_typos}

    all_files = []
    for root, dirs, files in os.walk(args.dir):
        if any([d.startswith('.') for d in root.split(os.sep)
                if d != '.']):
            # Ignore hidden directories
            # (which are assumed to start with '.')
            continue
        else:
            all_files.extend([os.path.join(root, filename)
                              for filename in files])

    file_beginnings_to_ignore = ['LICENSE', 'Makefile', 'TypoMakefile']
    file_endings_to_ignore = ['~', '.exe',
                              '.gz', '.jar', '.pdf', '.xml', '.zip']

    word_counter = Counter()

    print('Searching {} files'.format(len(all_files)))

    file_words = []

    known_words = get_known_words()

    searched_files = []

    for search_file in all_files:
        if any([search_file.endswith(e) for e in file_endings_to_ignore]):
            continue

        if any([search_file.split(os.sep)[-1].startswith(e)
                for e in file_beginnings_to_ignore]):
            continue

        searched_files.append(search_file)
        try:
            file_words_raw = get_words_in_file(search_file)
            file_words = [w.lower()
                          for w in file_words_raw]

            word_counter.update(file_words)

        except:
            pass

    print('Done searching files')
    sorted_words = list(word_counter.items())
    sorted_words = [k for (k, _) in sorted_words]
    sorted_words = [w for w in sorted_words if '_' not in w]
    sorted_words = [w for w in sorted_words if len(w) > 3]
    # sorted_words = [k for (k, v) in sorted(sorted_words, key=lambda x: x[-1])]
    sorted_words = [w for w in sorted_words if w not in known_words]
    sorted_words = [w for w in sorted_words if w not in typos]
    sorted_words = [w for w in sorted_words if not any(
        [str(d) in w for d in range(10)])]
    sorted_words = sorted(list(set(sorted_words)))

    print('Gathering candidates')
    
    typo_candidates = []

    
    for sorted_word in sorted_words:
        if len(sorted_word) > 20:
            continue

        # Idea: commonly used words aren't typos
        if word_counter[sorted_word] > 5:
            continue

        cs = candidates(sorted_word)
        if cs and len(cs) < 5 and sorted_word not in cs:
            if args.ignore_prepends:
                if cs.endswith(sorted_word):
                    continue

            if args.ignore_appends:
                if cs.startswith(sorted_word):
                    continue
            
            # Idea: the typo is made less frequently than the correct spelling
            in_text = [w for w in cs
                       if w in word_counter and word_counter[w] > word_counter[sorted_word] and word_counter[w] > 5]

            if not in_text:
                continue
            
            cnts = [(w, word_counter[w], word_counter[sorted_word]) for w in in_text]
            print('typo candidate: {}->{}'.format(sorted_word, ['{}'.format(x) for x in cnts]))
            typo_candidates.append((sorted_word, ', '.join(in_text)))

    print('Found {} typo candidates'.format(len(typo_candidates)))
    
    found_new_typos = []
    for typo_candidate in typo_candidates:
        res = is_new_typo(typo_candidate)
        if res is not None:
            found_new_typos.append(res)

    open('data/levenshtein_util_typos.txt', 'w').write('\n'.join(['{}->{}'.format(x, y) for (x, y) in found_new_typos]))