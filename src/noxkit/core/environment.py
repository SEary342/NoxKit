from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class EnvironmentManager:
    """Select explicit Nox backends for normal and matrix sessions."""

    normal_backend: str = "none"
    matrix_backend: str = "uv"

    def select(self, mode: Literal["normal", "matrix"]) -> str:
        """Return the configured backend for a known execution mode."""
        if mode == "normal":
            return self.normal_backend
        if mode == "matrix":
            return self.matrix_backend
        raise ValueError(f"unknown environment mode: {mode}")