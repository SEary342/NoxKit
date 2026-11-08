from typing import ClassVar


class BaseChecker:
    """Base command checker configured by its subclasses."""

    session_name: ClassVar[str]
    command_prefix: ClassVar[tuple[str, ...]] = ()

    def get_command(self, args: list[str]) -> list[str]:
        """Build the command to run the checker."""
        prefix = self.command_prefix or (self.session_name,)
        return [*prefix, *args]