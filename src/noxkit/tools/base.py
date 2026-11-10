class Tool:
    """Base command checker configured by its subclasses."""

    session_name: str
    command_prefix: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    default_args: tuple[str, ...] = ()
    description: str | None = None
    dependency_group: str | None = None

    def __init__(
        self,
        session_name: str | None = None,
        *,
        command_prefix: tuple[str, ...] | None = None,
        dependencies: tuple[str, ...] | None = None,
        default_args: tuple[str, ...] | None = None,
        description: str | None = None,
        dependency_group: str | None = None,
    ) -> None:
        configured_name = session_name or getattr(type(self), "session_name", None)
        if not configured_name:
            raise ValueError("a tool session name is required")
        self.session_name = configured_name
        self.command_prefix = (
            command_prefix
            if command_prefix is not None
            else getattr(type(self), "command_prefix", ())
        )
        self.dependencies = (
            dependencies
            if dependencies is not None
            else getattr(type(self), "dependencies", ())
        )
        self.default_args = (
            default_args
            if default_args is not None
            else getattr(type(self), "default_args", ())
        )
        self.description = (
            description
            if description is not None
            else getattr(type(self), "description", None)
        )
        self.dependency_group = (
            dependency_group
            if dependency_group is not None
            else getattr(type(self), "dependency_group", None)
        )

    def get_command(self, args: list[str]) -> list[str]:
        """Build the command to run the checker."""
        prefix = self.command_prefix or (self.session_name,)
        return [*prefix, *self.default_args, *args]