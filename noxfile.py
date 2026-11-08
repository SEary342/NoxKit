import sys
from pathlib import Path

import nox

SOURCE_ROOT = Path(__file__).parent / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from noxkit import Project
from noxkit.core import NoxKitEngine

nox.needs_version = ">=2026.10.20"
nox.options.default_venv_backend = "uv|virtualenv"

project = Project(lint=True, tests=False, coverage=False)
NoxKitEngine(project).register_sessions()


@nox.session
def check(session: nox.Session) -> None:
    """Validate configuration and package imports."""
    project.validate()
    session.install("-e", ".")
    session.run("python", "-m", "compileall", "-q", "src/noxkit")
    session.run(
        "python",
        "-c",
        "from noxkit import Project; Project().validate()",
    )
