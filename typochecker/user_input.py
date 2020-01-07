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

    def __init__(self, s):
        self.input = s.strip()
        return

    def quit(self):
        return self.input == '!q'

    def get_help(self):
        return self.input == '!h'

    def keep_original(self):
        return self.input == ''

    def ignore(self):
        return self.input.lower() == '!i'

    def accept_suggestion(self, commas_allowed=False):
        return any([c == self.input for c in '/!']) and not self.re_check(commas_allowed)

    def literal(self):
        return (not self.keep_original() and not self.accept_suggestion() and
                not any([c in self.input for c in '/!']))

    def re_check(self, commas_allowed=False):
        return not commas_allowed and ',' in self.input


class UserResponse(object):
    def __init__(self):
        return


class Keep(UserResponse):
    def __init__(self):
        super().__init__()
        return


class Quit(UserResponse):
    def __init__(self):
        super().__init__()
        return


class Ignore(UserResponse):
    def __init__(self, s):
        super().__init__()
        self.word = s
        return


class Literal(UserResponse):
    def __init__(self, s):
        super().__init__()
        self.word = s
        return
