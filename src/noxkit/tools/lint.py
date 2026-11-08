from noxkit.tools.base import BaseTool


class RuffChecker(BaseTool):
    """Check code style, formatting, and common errors with Ruff."""

    session_name = "ruff"
    command_prefix = ("ruff", "check")


class PylintChecker(BaseTool):
    """Analyze code for errors and code quality issues with Pylint."""

    session_name = "pylint"