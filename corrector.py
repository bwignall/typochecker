import argparse
import fileinput
import os
import re
import sys

# Assumption: long lines (e.g., in JSON files) should be skipped
MAX_LINE_LEN = 200


def get_typos(loc):
    print('opening {}'.format(loc))
    with open(loc, 'r') as f:
        ls = f.readlines()

    d = {}

    for line in ls:
        k, v = line.strip().split('->')
        d.update({k: v})

    return d


def get_typos_in_string(s, known_typos):
    """
    >>> get_typos_in_string('foo buzz', {'foo': 'bar', 'bazz': 'buzz'})
    ['foo']

    >>> get_typos_in_string('foo bazz', {'foo': 'bar', 'bazz': 'buzz'})
    ['bazz', 'foo']
    """
    words = re.findall(r'[\w]+', s)
    uniq_words = set(words)

    return sorted([w for w in uniq_words if w in known_typos])


def get_typos_in_file(f, known_typos):
    with open(f, 'r') as ff:
        lines = ff.readlines()

    return get_typos_in_string(' '.join(lines), known_typos)


def get_fix(line, typo_span, suggestion, orig):
    print(line)

    cnt = typo_span[1] - typo_span[0] + 1

    # assume tab <=> 4 spaces, to align '^'s with text
    ws_cnt = sum([4 if c == '\t' else 1 for c in line[:typo_span[0]]])
    print(' ' * ws_cnt + '^' * cnt)

    print('Suggestion: {}'.format(suggestion))

    response_raw = input(('Correction ("!h" for help), default to {}: '
                          ).format(suggestion))

    response = response_raw.strip()

    if response == '!q':
        sys.exit(1)

    if response == '':
        if ',' not in suggestion:
            return suggestion
        else:
            """Some suggestions have multiple alternatives,
            separated by commas; force to pick one"""
            return get_fix(line, typo_span, suggestion, orig)

    if response in '!/':
        return orig

    if response == '!h' or response.startswith('!'):
        print('Commands:\n'
              '\t!h for help\n'
              '\t!q to quit\n'
              '"!" or "/" to leave as-is\n'
              'leave blank and hit Enter to accept suggestion\n')
        return get_fix(line, typo_span, suggestion, orig)

    return response


def iterate_over_file(f, all_typos, found_typos):
    has_rewrites = False

    all_lines = []

    re_pat = re.compile(r'\W' + '|'.join(found_typos) + r'\W')

    with open(f, 'r') as fname:
        raw_lines = fname.readlines()

    for raw_line in raw_lines:
        line = raw_line

        m = re_pat.search(line)

        while m and (len(line) < MAX_LINE_LEN):
            matched_typo = m.group()[1:-1]

            fix = get_fix(line, m.span(),
                          all_typos[matched_typo], matched_typo)

            if fix == matched_typo:
                # If skip the fix, assume rest of line is acceptable
                break

            has_rewrites = True

            print('Before: {}'.format(line))
            line = re.sub(r'(\W)' + matched_typo + r'(\W)',
                          r'\1' + fix + r'\2',
                          line,
                          count=1)

            print('After: {}'.format(line))
            m = re_pat.search(line)

        all_lines.append(line)

    if has_rewrites:
        with open(f, 'w') as fname:
            sep = ''  # Original lines already have line-ending
            fname.write(sep.join(all_lines))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', help='Search this directory, recursively, to find files to check')
    parser.add_argument('-w', '--whitelist_word', action='append',
                        help='Do not consider this word a typo. Argument can be repeated')
    parser.add_argument('-W', '--whitelist_file', action='append',
                        help='A file containing words that should not be considered typos. Argument can be repeated')

    args = parser.parse_args()

    if not args.dir:
        all_files = [f.strip() for f in fileinput.input()]
    else:
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

    # By default, use typos gathered at
    # https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines
    TYPOS_LOC = os.path.join(os.path.dirname(__file__),
                             'data', 'wikipedia_common_misspellings.txt')
    EXTRA_TYPOS_LOC = os.path.join(os.path.dirname(__file__),
                                   'data', 'extra_endings.txt')

    print('Getting list of typos')
    typo_src = 'https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines'
    print('Information from {}'.format(typo_src))
    typos = {}
    for fs in [TYPOS_LOC, EXTRA_TYPOS_LOC]:
        typos.update(get_typos(fs))

    # Remove whitelisted words from typos

    for word in args.whitelist_word or []:
        del typos[word.lower()]

    for whitelist_file in args.whitelist_file or []:
        try:
            with open(whitelist_file, 'r') as ff:
                lines = ff.readlines()

            words = re.findall(r'[\w]+', ' '.join(lines))

            for word in words:
                del typos[word.lower()]

        except:
            print('Encountered problem while trying to trying to read whitelist file {}'.format(whitelist_file))

    # Remove some case sensitivity
    titled_typos = {k.title(): v.title() for k, v in typos.items()}
    typos.update(titled_typos)

    file_beginnings_to_ignore = ['LICENSE']
    file_endings_to_ignore = ['~', '.exe', '.gz', '.jar', '.pdf', '.xml', '.zip']

    for search_file in all_files:
        if any([search_file.endswith(e) for e in file_endings_to_ignore]):
            continue

        if any([search_file.split(os.sep)[-1].startswith(e)
                for e in file_beginnings_to_ignore]):
            continue

        try:
            file_typos = get_typos_in_file(search_file, typos)

            if file_typos:
                # print('file_typos: {}'.format(file_typos))
                print('Suggestions follow for file {}'.format(search_file))
                iterate_over_file(search_file, typos, file_typos)

        except:
            pass
