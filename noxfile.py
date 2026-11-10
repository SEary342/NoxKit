import sys
from pathlib import Path

import nox

SOURCE_ROOT = Path(__file__).parent / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from noxkit import NoxKitEngine, Project, Stage, Tool

nox.needs_version = ">=2026.10.20"
nox.options.default_venv_backend = "uv|virtualenv"

project = Project(
    stages=[
        Stage(name="lint", tools=["ruff", Tool("flake8"), "bandit"], parallel=True),
        Stage(
            name="type-check",
            tools=[
                Tool(
                    "ty",
                    command_prefix=("ty", "check"),
                )
            ],
        ),
        Stage(
            name="black-version",
            tools=[
                Tool(
                    "black",
                    default_args=("--version",),
                )
            ],
        ),
    ],
)
NoxKitEngine(project).register_sessions()
