from noxkit.tools import BaseTool


class RuffFormat(BaseTool):
    session_name = "ruff-format"
    command_prefix = ("ruff", "format")
