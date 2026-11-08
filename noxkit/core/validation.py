from noxkit.project import Project


def validate_project(project: Project) -> None:
    """Validate a project's declarative configuration."""
    project.validate()