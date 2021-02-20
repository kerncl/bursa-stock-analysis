class EdarException(Exception):
    pass


class WebException(EdarException):
    pass


class ScriptException(EdarException):
    pass


class WebLoadException(WebException):
    pass


class WebAccessException(WebException):
    pass


class InvalidXpathException(WebException):
    pass