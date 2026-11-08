from noxkit.checkers.base import BaseChecker


class MypyChecker(BaseChecker):
    session_name = "mypy"


class PyrightChecker(BaseChecker):
    session_name = "pyright"