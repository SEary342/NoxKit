from noxkit.checkers.base import BaseChecker


class RuffChecker(BaseChecker):
    session_name = "ruff"
    command_prefix = ("ruff", "check")


class PylintChecker(BaseChecker):
    session_name = "pylint"