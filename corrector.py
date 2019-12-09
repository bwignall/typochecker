import argparse
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
        d.update({k.title(): v.title()})

    return d


def get_typos_in_file(f, known_typos):
    with open(f, 'r') as ff:
        lines = ff.readlines()

    words = re.findall(r'[\w]+', ' '.join(lines))
    uniq_words = set(words)

    return [w for w in uniq_words if w in known_typos]


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
    parser.add_argument('-f', '--file',
                        default='all_git_files_for_autocorrect.txt')

    args = parser.parse_args()

    with open(args.file, 'r') as datafile:
        all_files = [w.strip() for w in datafile.readlines()]

    # By default, use typos gathered at
    # https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines
    TYPOS_LOC = os.path.join(os.path.dirname(__file__),
                             'data', 'wikipedia_common_misspellings.txt')

    print('Getting list of typos')
    print('Information from https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines')
    typos = get_typos(TYPOS_LOC)

    file_beginnings_to_ignore = ['LICENSE']
    file_endings_to_ignore = ['.exe', '.jar', '.xml', '.zip']

    for search_file in all_files:
        if any([search_file.endswith(e) for e in file_endings_to_ignore]):
            continue

        if any([search_file.split(os.sep)[-1].startswith(e)
                for e in file_endings_to_ignore]):
            continue

        try:
            file_typos = get_typos_in_file(search_file, typos)

            if file_typos:
                print('file_typos: {}'.format(file_typos))
                print('Suggestions follow for file {}'.format(search_file))
                iterate_over_file(search_file, typos, file_typos)

        except:
            pass
