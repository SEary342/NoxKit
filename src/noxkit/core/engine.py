from inspect import getdoc

import nox

from noxkit.tools import BaseTool, RuffChecker
from noxkit.matrix.engine import MatrixEngine
from noxkit.project import Project


class NoxKitEngine:
    """Orchestrates the generation of Nox sessions."""
    
    def __init__(self, project: Project):
        self.project = project
        self.matrix_engine = MatrixEngine()

    def register_sessions(self) -> None:
        """Register Nox sessions for the configured project checks."""
        self.project.validate()

        # TODO iterate over config items and auto-register
        if self.project.lint:
            self._register_tool(RuffChecker())

    def _register_tool(self, checker: BaseTool) -> None:
        args = self.project.args.get(checker.session_name, [])
        dependencies = self.project.dependencies.get(
            checker.session_name,
            [checker.session_name],
        )

        def run_checker(session: nox.Session) -> None:
            if dependencies:
                session.install(*dependencies)
            session.run(*checker.get_command(args))

        run_checker.__doc__ = getdoc(type(checker)) or f"Run {checker.session_name}."
        nox.session(name=checker.session_name, allow_parallel=True)(run_checker)