# Use heuristics inspired by Peter's Norvig's spelling corrector,
# https://norvig.com/spell-correct.html
# https://github.com/norvig/pytudes/blob/master/py/spell.py

import argparse
import os
from collections import Counter

from utils import candidates, get_words_in_file, get_default_typos

# Assumption: long lines (e.g., in JSON files) should be skipped
MAX_LINE_LEN = 200


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
    except KeyboardInterrupt:
        return None


def get_known_words(loc='/usr/share/dict/american-english'):
    return set([w.lower() for w in get_words_in_file(loc)])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Search this directory, recursively, to find files to check')

    args = parser.parse_args()

    typos = get_default_typos()

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

    added_words = []
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
                          for w in file_words_raw if w.lower() not in known_words]

            word_counter.update(file_words)

            added_words.extend(file_words)
        except OSError:
            pass

    print('Done searching files')
    sorted_words_0 = [k for (k, v) in sorted(
        word_counter.items(), key=lambda x: x[-1])]
    sorted_words_1 = [w for w in sorted_words_0 if w not in known_words]
    sorted_words_2 = [w for w in sorted_words_1 if '_' not in w]
    sorted_words_3 = [w for w in sorted_words_2 if not any(
        [str(d) in w for d in range(10)])]
    sorted_words_4 = [w for w in sorted_words_3 if len(w) > 3]
    sorted_words = [w for w in sorted_words_4 if w not in typos]

    typo_candidates = []

    for sorted_word in sorted_words:
        cs = candidates(sorted_word)
        if cs and len(cs) < 5 and sorted_word not in cs:
            typo_candidates.append((sorted_word, ', '.join(cs)))

    found_new_typos = []
    for typo_candidate in typo_candidates:
        res = is_new_typo(typo_candidate)
        if res is not None:
            found_new_typos.append(res)

    open('../data/norvig_util_typos.txt', 'w').write('\n'.join(['{}->{}'.format(x, y) for (x, y) in found_new_typos]))
