import argparse
import fileinput
import os
import re
from typing import Any, Dict, List, Optional, Pattern, Tuple

from typochecker.suggestion_response import (
    AlwaysRespondIgnore,
    Ignore,
    Keep,
    Quit,
    Response,
    SuggestionResponse,
    Unknown,
)
from typochecker.user_input import UserResponse
from typochecker.utils import get_visible_subdirs, parse_typos_file

# Assumption: long lines (e.g., in JSON files) should be skipped
MAX_LINE_LEN = 200


def get_typos_in_string(s: str, known_typos: Dict[str, str]) -> List:
    """
    >>> get_typos_in_string('foo buzz', {'foo': 'bar', 'bazz': 'buzz'})
    ['foo']

    >>> get_typos_in_string('foo bazz', {'foo': 'bar', 'bazz': 'buzz'})
    ['bazz', 'foo']
    """
    words = re.findall(r"[\w]+", s)
    uniq_words = set(words)

    return sorted([w for w in uniq_words if w.lower() in known_typos])


def get_typos_in_file(f: str, known_typos: Dict[str, str]) -> List:
    with open(f, "r") as ff:
        lines = ff.readlines()

    return get_typos_in_string(" ".join(lines), known_typos)


def get_fix(
    line: str,
    typo_span: Tuple[int, int],
    suggestion: str,
    orig: str,
    responder: SuggestionResponse,
) -> Response:
    print(line)

    cnt = typo_span[1] - typo_span[0] + 1

    # assume tab <=> 4 spaces, to align '^'s with text
    ws_cnt = sum(4 if c == "\t" else 1 for c in line[: typo_span[0]])
    print(" " * ws_cnt + "^" * cnt)

    print("Suggestion: {}".format(suggestion))

    prompt = 'Correction ("!h" for help), default to {}: '.format(suggestion)

    response = responder.get_response(line, typo_span, suggestion, orig, prompt)

    if not isinstance(response, Unknown):
        return response
    else:
        return get_fix(line, typo_span, suggestion, orig, responder)


def get_fixed_line(line, matched_typo, fix):
    """
    >>> get_fixed_line('There isss a typo', 'isss', 'is')
    'There is a typo'

    >>> get_fixed_line('There is a tpyo', 'tpyo', 'typo')
    'There is a typo'

    >>> get_fixed_line('Theer is a typo', 'Theer', 'There')
    'There is a typo'
    """
    if re.search(r"^" + matched_typo + r"(\W)", line):
        return re.sub(r"^" + matched_typo + r"(\W)", fix + r"\1", line, count=1)
    elif re.search(r"(\W)" + matched_typo + r"$", line):
        return re.sub(r"(\W)" + matched_typo + r"$", r"\1" + fix, line, count=1)
    elif re.search(r"(\W)" + matched_typo + r"(\W)", line):
        return re.sub(
            r"(\W)" + matched_typo + r"(\W)", r"\1" + fix + r"\2", line, count=1
        )

    return line


def iterate_over_lines(
    raw_lines: List[str],
    all_typos: Dict[str, str],
    found_typos: List[str],
    responder: SuggestionResponse,
) -> Tuple[List[str], bool]:
    has_rewrites = False

    all_lines = []

    def get_regex(typos: List[str]) -> Pattern:
        return re.compile("|".join(r"\W" + found_typo + r"\W" for found_typo in typos))

    re_pat = get_regex(found_typos)

    for raw_line in raw_lines:
        line = raw_line

        m = re_pat.search(line)

        while found_typos and m and (len(line) < MAX_LINE_LEN):
            matched_typo = re.sub("[^a-zA-Z]+", "", m.group())

            if matched_typo not in all_typos and matched_typo.lower() not in all_typos:
                fix = Ignore(matched_typo)
            else:
                fix = get_fix(
                    line,
                    m.span(),
                    all_typos.get(matched_typo, None)
                    or all_typos[matched_typo.lower()],
                    matched_typo,
                    responder,
                )

            if isinstance(fix, Quit):
                # This will abandon any work so far on the file/lines
                return raw_lines, False
            elif isinstance(fix, Keep):
                # If skip the fix, assume rest of line is acceptable
                break
            elif isinstance(fix, Ignore):
                to_ignore = fix.word
                found_typos = [t for t in found_typos if t != to_ignore]

                # Don't look for this "typo" in the future
                all_typos.pop(to_ignore, None)
                all_typos.pop(to_ignore.lower(), None)
                all_typos.pop(to_ignore.title(), None)
                all_typos.pop(to_ignore.upper(), None)

                re_pat = get_regex(found_typos)
                m = re_pat.search(line)

                continue

            has_rewrites = True

            fix = fix.word

            print("Before: {}".format(line))
            line = get_fixed_line(line, matched_typo, fix)

            print("After:  {}".format(line))
            m = re_pat.search(line)

        all_lines.append(line)

    return all_lines, has_rewrites


def iterate_over_file(
    f: str,
    all_typos: Dict[str, str],
    found_typos: List[str],
    responder: SuggestionResponse,
) -> Optional[Any]:
    with open(f, "r") as fname:
        raw_lines = fname.readlines()

    all_lines, has_rewrites = iterate_over_lines(
        raw_lines, all_typos, found_typos, responder
    )

    if isinstance(all_lines, Quit):
        return all_lines

    if has_rewrites:
        with open(f, "w") as fname:
            sep = ""  # Original lines already have line-ending
            fname.write(sep.join(all_lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--dir", help="Search this directory, recursively, to find files to check"
    )
    parser.add_argument(
        "-w",
        "--whitelist_word",
        action="append",
        help="Do not consider this word a typo. Argument can be repeated",
    )
    parser.add_argument(
        "-W",
        "--whitelist_file",
        action="append",
        help="A file containing words that should not be considered typos. Argument can be repeated",
    )
    parser.add_argument(
        "--ignore-all",
        action="store_true",
        help="Ignore all suggestions (useful for debugging)",
    )

    args = parser.parse_args()

    if not args.dir:
        all_files = [f.strip() for f in fileinput.input()]
    else:
        all_files = get_visible_subdirs(args.dir)

    # By default, use typos gathered at
    # https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines
    TYPOS_LOC = os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "data",
        "wikipedia_common_misspellings.txt",
    )
    EXTRA_TYPOS_LOC = os.path.join(
        os.path.dirname(__file__), os.pardir, "data", "extra_endings.txt"
    )

    print("Getting list of typos")
    typo_src = "https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines"
    print("Information from {}".format(typo_src))
    typos = {}
    for fs in [TYPOS_LOC, EXTRA_TYPOS_LOC]:
        typos.update(parse_typos_file(fs))

    # Remove whitelisted words from typos

    for word in args.whitelist_word or []:
        del typos[word.lower()]

    for whitelist_file in args.whitelist_file or []:
        try:
            with open(whitelist_file, "r") as ff:
                lines = ff.readlines()

        except OSError:
            print(
                "Encountered problem while trying to trying to read whitelist file {}".format(
                    whitelist_file
                )
            )

        words = re.findall(r"[\w]+", " ".join(lines))

        for word in words:
            del typos[word.lower()]

    # Remove some case sensitivity
    titled_typos = {k.title(): v.title() for k, v in typos.items()}
    typos.update(titled_typos)
    upper_typos = {k.upper(): v.upper() for k, v in typos.items()}
    typos.update(upper_typos)

    file_beginnings_to_ignore = ["LICENSE"]
    file_endings_to_ignore = ["~", ".exe", ".gz", ".jar", ".pdf", ".xml", ".zip"]

    print("Will search through {} files".format(len(all_files)))

    if args.ignore_all:
        responder = AlwaysRespondIgnore()
    else:
        responder = UserResponse()

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

        try:
            # print('Searching file: {}'.format(search_file))
            file_typos = get_typos_in_file(search_file, typos)

            if file_typos:
                print("Suggestions follow for file {}".format(search_file))
                print("file_typos: {}".format(file_typos))
                res = iterate_over_file(search_file, typos, file_typos, responder)

                if isinstance(res, Quit):
                    break

        except OSError:
            pass

        except UnicodeDecodeError:
            print("### Experienced an error with file {}".format(search_file))

        except EOFError:
            pass
