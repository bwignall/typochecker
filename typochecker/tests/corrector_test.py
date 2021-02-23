import unittest

import typochecker.corrector as c
from typochecker.suggestion_response import (
    AlwaysRespondAccept,
    AlwaysRespondIgnore,
    AlwaysRespondKeep,
)


class TestTrivialLine(unittest.TestCase):
    def test_1(self):
        file_typos = ["tpyo"]
        typos = {"tpyo": "typo"}

        # Ensure nothing throws an exception
        for responder in [
            AlwaysRespondAccept(),
            AlwaysRespondIgnore(),
            AlwaysRespondKeep(),
        ]:
            line = "line with a typo : {}".format(file_typos[0])
            c.iterate_over_lines([line], typos, file_typos, responder)


class TestMixedCapitalization(unittest.TestCase):
    def test_1(self):
        file_typos = ["tpyo", "TPyo", "tPyo"]

        # Ensure nothing throws an exception
        for responder in [
            AlwaysRespondAccept(),
            AlwaysRespondIgnore(),
            AlwaysRespondKeep(),
        ]:
            for file_typo in file_typos:
                typos = {"tpyo": "typo, typee"}

                line = "line with a typo : {}".format(file_typo)
                c.iterate_over_lines([line], typos, [file_typo], responder)


class TestMultipleSuggestions(unittest.TestCase):
    def test_1(self):
        file_typos = ["tpyo", "TPyo", "tPyo"]

        # Ensure nothing throws an exception
        for responder in [
            AlwaysRespondAccept(),
            AlwaysRespondIgnore(),
            AlwaysRespondKeep(),
        ]:
            for file_typo in file_typos:
                typos = {"tpyo": "typo, typee"}

                line = "line with a typo : {}".format(file_typo)
                c.iterate_over_lines([line], typos, [file_typo], responder)


class TestMultipleVersionsInLine(unittest.TestCase):
    def test_1(self):
        file_typos = ["THead", "thead"]

        # Ensure nothing throws an exception
        for responder in [
            AlwaysRespondAccept(),
            AlwaysRespondIgnore(),
            AlwaysRespondKeep(),
        ]:
            for file_typo in file_typos:
                typos = {"tpyo": "typo, typee"}

                line = "line with multiple typo variants : {} {} {} {}".format(
                    file_typo, file_typo.lower(), file_typo.upper(), file_typo.title()
                )
                c.iterate_over_lines([line], typos, [file_typo], responder)


if __name__ == "__main__":
    unittest.main()
