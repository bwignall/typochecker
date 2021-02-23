from typochecker.suggestion_response import (
    Ignore,
    Keep,
    Literal,
    Quit,
    Response,
    SuggestionResponse,
    Unknown,
)


class UserInput(object):
    """
    >>> u = UserInput('')
    >>> u.quit()
    False
    >>> u.accept_suggestion()
    False
    >>> u.keep_original()
    True

    >>> u = UserInput('/')
    >>> u.quit()
    False
    >>> u.re_check()
    False
    >>> u.accept_suggestion()
    True
    >>> u.literal()
    False
    >>> u.keep_original()
    False

    >>> u = UserInput('abc')
    >>> u.quit()
    False
    >>> u.accept_suggestion()
    False
    >>> u.keep_original()
    False
    >>> u.literal()
    True

    >>> u = UserInput('a, b')
    >>> u.re_check()
    True
    """

    def __init__(self, s: str) -> None:
        self.input = s.strip()
        return

    def quit(self) -> bool:
        return self.input == "!q"

    def get_help(self) -> bool:
        return self.input == "!h"

    def keep_original(self) -> bool:
        return self.input == ""

    def ignore(self):
        return self.input.lower() == "!i"

    def accept_suggestion(self, commas_allowed: bool = False) -> bool:
        return any([c == self.input for c in "/!"]) and not self.re_check(
            commas_allowed
        )

    def literal(self) -> bool:
        return (
            not self.keep_original()
            and not self.accept_suggestion()
            and not any([c in self.input for c in "/!"])
        )

    def re_check(self, commas_allowed: bool = False) -> bool:
        return not commas_allowed and "," in self.input


class UserResponse(SuggestionResponse):
    def __init__(self):
        super().__init__()

    def get_response(self, line, typo_span, suggestion, orig, prompt) -> Response:
        response_raw = input(prompt)

        response = UserInput(response_raw)

        if response.quit():
            return Quit()
        elif response.get_help():
            print(
                "Commands:\n"
                "\t!h for help\n"
                "\t!q to quit\n"
                '\t"!" or "/" to accept suggestion\n'
                "\tleave blank and hit Enter to leave as-is\n"
                '\t"!i" to ignore suggestion for rest of session'
            )
            return Unknown()
        elif response.re_check():
            """Some suggestions have multiple alternatives,
            separated by commas; force to pick one"""
            return Unknown()
        elif response.accept_suggestion() and "," not in suggestion:
            return Literal(suggestion)
        elif response.literal():
            return Literal(response.input)
        elif response.keep_original():
            return Keep()
        elif response.ignore():
            return Ignore(orig)
