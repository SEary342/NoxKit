from noxkit.tools.base import BaseTool


class MypyChecker(BaseTool):
    """Check Python type annotations with Mypy."""

    session_name = "mypy"


class PyrightChecker(BaseTool):
    """Check Python type annotations with Pyright."""

    session_name = "pyright"