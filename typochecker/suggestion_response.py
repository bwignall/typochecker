class Response(object):
    def __init__(self) -> None:
        return


class Keep(Response):
    def __init__(self) -> None:
        super().__init__()
        return


class Quit(Response):
    def __init__(self):
        super().__init__()
        return


class Ignore(Response):
    def __init__(self, s):
        super().__init__()
        self.word = s
        return


class Literal(Response):
    def __init__(self, s):
        super().__init__()
        self.word = s
        return


class Unknown(Response):
    def __init__(self):
        super().__init__()
        return


class SuggestionResponse(object):
    def __init__(self):
        pass

    def get_response(self, line, typo_span, suggestion, orig, prompt) -> Response:
        pass


class AlwaysRespondAccept(SuggestionResponse):
    def __init__(self):
        super().__init__()

    def get_response(self, line, typo_span, suggestion, orig, prompt):
        return Literal(suggestion)


class AlwaysRespondKeep(SuggestionResponse):
    def __init__(self):
        super().__init__()

    def get_response(self, line, typo_span, suggestion, orig, prompt):
        return Keep()


class AlwaysRespondIgnore(SuggestionResponse):
    def __init__(self):
        super().__init__()

    def get_response(self, line, typo_span, suggestion, orig, prompt):
        return Ignore(orig)
