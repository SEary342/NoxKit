import sys
from pathlib import Path

import nox

sys.path.insert(0, str(Path(__file__).parent))

from noxkit import Project
from noxkit.checkers import RuffChecker

nox.needs_version = ">=2026.10.20"
nox.options.default_venv_backend = "uv|virtualenv"

project = Project(lint=False, tests=False, coverage=False)


@nox.session
def check(session: nox.Session) -> None:
    """Validate configuration and run the configured NoxKit checker."""
    project.validate()
    session.run("python", "-m", "compileall", "-q", "noxkit")
    session.run(
        "python",
        "-c",
        "from noxkit import Project; Project().validate()",
    )
    session.install("ruff")
    checker = RuffChecker()
    session.run(*checker.get_command(["noxkit"]))
