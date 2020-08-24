# Use heuristics inspired by Peter's Norvig's spelling corrector,
# https://norvig.com/spell-correct.html
# https://github.com/norvig/pytudes/blob/master/py/spell.py

import argparse
import os
from collections import Counter

from typochecker.utils import (
    candidates,
    get_default_typos,
    get_visible_subdirs,
    get_words_in_file,
)

# Assumption: long lines (e.g., in JSON files) should be skipped
MAX_LINE_LEN = 200


def order_typo_candidates(tcs):
    """
    Order typo candidates, according to which have the highest maximum ratio
    between a candidate's count and a (suspected) typo's count. The idea is that
    the rarer a "typo" is, the more likely it is to be a genuine typo.

    Input:
    - tcs : list of tuples, [(typo, [(candidate, candidate_cnt, typo_cnt)])]

    Output:
    - ordered list of tuples, [(typo, [(candidate, candidate_cnt, typo_cnt)])]

    >>> t1 = ('t1', [('c1', 10, 1), ('c2', 11, 1)])
    >>> t2 = ('t2', [('c1', 10, 4)])
    >>> t3 = ('t3', [('c1', 10, 2), ('c3', 100, 99)])
    >>> tcs = [t1, t2, t3]
    >>> order_typo_candidates(tcs)
    [('t1', [('c1', 10, 1), ('c2', 11, 1)]), ('t3', [('c1', 10, 2), ('c3', 100, 99)]), ('t2', [('c1', 10, 4)])]
    """
    return sorted(
        tcs, reverse=True, key=lambda x: max([cc / tc for (_, cc, tc) in x[1]])
    )


def is_new_typo(suspected_typo):
    typo, correction = suspected_typo
    try:
        response_raw = input(
            '{}->{} ("!" to accept, "" to ignore, "!q" to quit): '.format(
                typo, correction
            )
        )
        if response_raw == "!q":
            # Quit
            return response_raw
        elif response_raw.startswith("!") or response_raw == "/":
            return suspected_typo
        elif len(response_raw) > 1:
            return typo, response_raw
        else:
            return None
    except KeyboardInterrupt:
        return None


def get_known_words(loc="/usr/share/dict/american-english"):
    return set([w.lower() for w in get_words_in_file(loc)])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "dir", help="Search this directory, recursively, to find files to check"
    )
    parser.add_argument(
        "--ignore-prepends",
        action="store_true",
        help="If set, ignore suggestions where characters are only added to the front",
    )
    parser.add_argument(
        "--ignore-appends",
        action="store_true",
        help="If set, ignore suggestions where characters are only added to the end",
    )

    args = parser.parse_args()

    typos = get_default_typos()

    all_files = get_visible_subdirs(args.dir)

    file_beginnings_to_ignore = ["LICENSE", "Makefile", "TypoMakefile"]
    file_endings_to_ignore = ["~", ".exe", ".gz", ".jar", ".pdf", ".xml", ".zip"]

    word_counter = Counter()

    print("Searching {} files".format(len(all_files)))

    file_words = []

    known_words = get_known_words()

    searched_files = []

    for search_file in all_files:
        if any([search_file.endswith(e) for e in file_endings_to_ignore]):
            continue

        if any(
            [
                search_file.split(os.sep)[-1].startswith(e)
                for e in file_beginnings_to_ignore
            ]
        ):
            continue

        searched_files.append(search_file)
        try:
            file_words_raw = get_words_in_file(search_file)
            file_words = [w.lower() for w in file_words_raw]

            word_counter.update(file_words)

        except OSError:
            pass
        except UnicodeDecodeError:
            pass

    print("Done searching files")
    sorted_words = list(word_counter.items())
    sorted_words = [k for (k, _) in sorted_words]
    sorted_words = [w for w in sorted_words if "_" not in w]
    sorted_words = [w for w in sorted_words if len(w) > 3]
    # sorted_words = [k for (k, v) in sorted(sorted_words, key=lambda x: x[-1])]
    sorted_words = [w for w in sorted_words if w not in known_words]
    sorted_words = [w for w in sorted_words if w not in typos]
    sorted_words = [
        w for w in sorted_words if not any([str(d) in w for d in range(10)])
    ]
    sorted_words = sorted(list(set(sorted_words)))

    print("Gathering candidates")

    typo_candidates = []

    ascii_letters = "abcdefghijklmnopqrstuvwxyz"
    assert 26 == len(
        ascii_letters
    ), "Should have 26 letters in alphabet, not {}".format(len(ascii_letters))

    for sorted_word in sorted_words:
        if len(sorted_word) > 20:
            continue

        if any([c not in ascii_letters for c in sorted_word]):
            continue

        # Idea: commonly used words aren't typos
        if word_counter[sorted_word] > 5:
            continue

        cs = candidates(sorted_word)

        if args.ignore_prepends:
            cs = [
                c
                for c in cs
                if not c.endswith(sorted_word) and not sorted_word.startswith(c)
            ]

        if args.ignore_appends:
            cs = [
                c
                for c in cs
                if not c.startswith(sorted_word) and not sorted_word.endswith(c)
            ]

        if cs and len(cs) < 5 and sorted_word not in cs:
            # Idea: the typo is made less frequently than the correct spelling
            in_text = [
                w
                for w in cs
                if w in word_counter
                and word_counter[w] > word_counter[sorted_word]
                and word_counter[w] > 10
            ]

            if not in_text:
                continue

            cnts = [(w, word_counter[w], word_counter[sorted_word]) for w in in_text]
            print(
                "typo candidate: {}->{}".format(
                    sorted_word, ["{}".format(x) for x in cnts]
                )
            )
            typo_candidates.append((sorted_word, cnts, ", ".join(in_text)))

    print("Found {} typo candidates".format(len(typo_candidates)))

    found_new_typos = []
    for (typo, _, typo_candidates) in order_typo_candidates(typo_candidates):
        res = is_new_typo((typo, typo_candidates))
        if res == "!q":
            break
        if res is not None:
            found_new_typos.append(res)

    open("data/levenshtein_util_typos.txt", "w").write(
        "\n".join(["{}->{}".format(x, y) for (x, y) in found_new_typos])
    )
