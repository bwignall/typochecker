import argparse
import os
import sys

from typochecker.utils import parse_typos_file

# Assumption: long lines (e.g., in JSON files) should be skipped
MAX_LINE_LEN = 200


def get_addition(all_typos, known_ending, unknown_ending):
    new_defns = {}

    for k, v in all_typos.items():
        kk, ku = k + known_ending, k + unknown_ending
        if (kk in all_typos) and (ku not in all_typos):
            print("{} -> {}".format(k, v))
            print("{} -> {}".format(kk, all_typos[kk]))

            suggestion = v + unknown_ending
            print("{} -> ???".format(ku))
            print("Naive suggestion: {}".format(suggestion))

            try:
                response_raw = input(
                    ('Correction ("!h" for help), default to {}: ').format(suggestion)
                )
            except KeyboardInterrupt:
                continue

            response = response_raw.strip()

            if response == "!q":
                sys.exit(1)

            if response == "":
                if "," not in suggestion:
                    new_defns[ku] = suggestion
                    print("Updated additions: {}".format(new_defns))

            if response in "!/":
                continue

            if response == "!h" or response.startswith("!"):
                print(
                    "Commands:\n"
                    "\t!h for help\n"
                    "\t!q to quit\n"
                    '"!" or "/" to leave as-is\n'
                    "leave blank and hit Enter to accept suggestion\n"
                )
                sys.exit(1)

            new_defns[ku] = response
            print("Updated additions: {}".format(new_defns))

    return new_defns


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    args = parser.parse_args()

    # By default, use typos gathered at
    # https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines
    TYPOS_LOC = os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "data",
        "wikipedia_common_misspellings.txt",
    )

    typos = parse_typos_file(TYPOS_LOC)

    added_d = get_addition(typos, "s", "d")
    added_s = get_addition(typos, "d", "s")

    with open(
        os.path.join(os.path.dirname(__file__), os.pardir, "data", "extra_endings.txt"),
        "w",
    ) as f:
        txt = "\n".join(
            ["{}->{}".format(k, v) for k, v in {**added_d, **added_s}.items()]
        )
        f.writelines(txt)
