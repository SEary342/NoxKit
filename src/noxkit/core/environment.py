from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EnvironmentManager:
    """Selects the project's existing environment or a matrix backend."""

    backend: str = "uv"

    def select(self, project_manager: str | None = None) -> str:
        """Choose an environment backend for the requested project manager."""
        raise NotImplementedError("Environment selection is not implemented yet")