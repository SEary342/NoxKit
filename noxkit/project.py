from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Project:
    """Declarative configuration for NoxKit-managed project checks."""

    python: list[str] = field(default_factory=list)
    lint: bool = True
    tests: bool = True
    coverage: bool = True
    compatibility: dict[str, Any] = field(default_factory=dict)
    args: dict[str, list[str]] = field(default_factory=dict)
    env: dict[str, str] = field(default_factory=dict)
    exclude: list[dict[str, Any]] = field(default_factory=list)
    skip_combination: Callable[[dict[str, Any]], bool] | None = None
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    stages: list[Any] = field(default_factory=list)
    max_concurrency: int | None = None

    def validate(self) -> None:
        """Validate the configuration before sessions are generated."""
        if self.max_concurrency is not None and self.max_concurrency < 1:
            raise ValueError("max_concurrency must be a positive integer")
        if any(not isinstance(version, str) or not version for version in self.python):
            raise ValueError("python versions must be non-empty strings")