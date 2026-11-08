from noxkit.tools import BaseTool


class PytestChecker(BaseTool):
    """Run Pytest"""

    session_name = "pytest"


class PytestCoverageChecker(BaseTool):
    """Run Pytest with Coverage"""

    session_name = "pytest"
    command_prefix = ("pytest", "coverage")
