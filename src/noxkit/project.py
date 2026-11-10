from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from noxkit.tools import Tool


@dataclass
class Stage:
    """A named group of tools in the project execution pipeline."""

    name: str
    tools: list[str | Tool] = field(default_factory=list)
    parallel: bool = True


@dataclass
class Project:
    """Declarative configuration for NoxKit-managed project checks."""

    python: list[str] = field(default_factory=list)
    compatibility: dict[str, Any] = field(default_factory=dict)
    args: dict[str, list[str]] = field(default_factory=dict)
    env: dict[str, str] = field(default_factory=dict)
    exclude: list[dict[str, Any]] = field(default_factory=list)
    skip_combination: Callable[[dict[str, Any]], bool] | None = None
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    stages: list[Stage] = field(default_factory=list)
    max_concurrency: int | None = None

    def validate(self) -> None:
        """Validate the configuration before sessions are generated."""
        if self.max_concurrency is not None and self.max_concurrency < 1:
            raise ValueError("max_concurrency must be a positive integer")
        if any(not isinstance(version, str) or not version for version in self.python):
            raise ValueError("python versions must be non-empty strings")
        stage_names: set[str] = set()
        configured_tools: set[str] = set()
        for stage in self.stages:
            if not isinstance(stage, Stage):
                raise TypeError("stages must contain Stage instances")
            if not isinstance(stage.name, str):
                raise TypeError("stage names must be strings")
            if not stage.name.strip():
                raise ValueError("stage names must be non-empty strings")
            if stage.name in stage_names:
                raise ValueError(f"duplicate stage name: {stage.name}")
            stage_names.add(stage.name)
            if not isinstance(stage.tools, list):
                raise TypeError(f"stage '{stage.name}' tools must be a list")
            if not stage.tools:
                raise ValueError(f"stage '{stage.name}' must contain at least one tool")
            if not isinstance(stage.parallel, bool):
                raise TypeError(f"stage '{stage.name}' parallel must be a boolean")
            for tool in stage.tools:
                if isinstance(tool, str):
                    if not tool.strip():
                        raise ValueError("tool names must be non-empty strings")
                    session_name = tool
                elif isinstance(tool, Tool):
                    session_name = tool.session_name
                else:
                    raise TypeError("stage tools must be names or Tool instances")
                if session_name in configured_tools:
                    raise ValueError(
                        f"tool may only appear once in the pipeline: {session_name}"
                    )
                configured_tools.add(session_name)