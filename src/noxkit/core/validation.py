import nox

from noxkit.project import Project
from noxkit.tools import Tool


def validate_project(project: Project) -> None:
    """Validate a project's declarative configuration."""
    project.validate()


def validate_tool_installed(session: nox.Session, tool: Tool) -> None:
    """Check that a tool executable is available in its Nox environment."""
    executable = tool.command_prefix[0] if tool.command_prefix else tool.session_name
    session.run(
        "python",
        "-c",
        "import shutil, sys; "
        "executable = sys.argv[1]; "
        "sys.exit(0 if shutil.which(executable) else "
        "f\"Required tool '{executable}' is not installed\")",
        executable,
    )