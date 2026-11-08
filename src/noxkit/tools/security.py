from noxkit.tools.base import BaseTool


class BanditChecker(BaseTool):
    """Scan Python code for common security issues with Bandit."""

    session_name = "bandit"