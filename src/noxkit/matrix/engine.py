import re
from itertools import product
from typing import Any

import nox

from noxkit.core.environment import EnvironmentManager
from noxkit.core.reporting import Reporter
from noxkit.project import Project


class MatrixEngine:
    """Generates and registers isolated compatibility matrix sessions."""

    def __init__(self, environment_manager: EnvironmentManager | None = None):
        self.environment_manager = environment_manager or EnvironmentManager()

    @staticmethod
    def is_configured(project: Project) -> bool:
        return bool(project.python or project.compatibility)

    def combinations(self, project: Project) -> list[dict[str, str]]:
        dimensions = dict(project.compatibility)
        if project.python:
            if "python" in dimensions:
                raise ValueError("python versions must be configured with Project.python")
            dimensions = {"python": project.python, **dimensions}
        combinations = self.generate_combinations(dimensions)
        combinations = self.apply_exclusions(combinations, project.exclude)
        if project.skip_combination is not None:
            combinations = [
                combination
                for combination in combinations
                if not project.skip_combination(combination)
            ]
        return combinations

    def session_names(self, project: Project) -> list[str]:
        return [
            self._session_name(combination)
            for combination in self.combinations(project)
        ]

    def generate_combinations(
        self, compatibility_config: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate every combination from explicit, non-empty version lists."""
        if not isinstance(compatibility_config, dict):
            raise TypeError("compatibility dimensions must be a dictionary")
        if not compatibility_config:
            return []

        dimensions: list[tuple[str, list[str]]] = []
        for name, versions in compatibility_config.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    "compatibility dimension names must be non-empty strings"
                )
            if not isinstance(versions, list) or not versions:
                raise ValueError(
                    f"compatibility dimension '{name}' must be a non-empty list "
                    "of explicit versions"
                )
            if any(not isinstance(version, str) or not version for version in versions):
                raise ValueError(
                    f"compatibility dimension '{name}' versions must be non-empty strings"
                )
            dimensions.append((name, versions))

        names = [name for name, _ in dimensions]
        return [
            dict(zip(names, combination, strict=True))
            for combination in product(*(versions for _, versions in dimensions))
        ]

    def apply_exclusions(
        self,
        combinations: list[dict[str, Any]],
        exclusions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Filter out explicitly excluded combinations."""
        return [
            combination
            for combination in combinations
            if not any(
                exclusion
                and all(
                    combination.get(name) == version
                    for name, version in exclusion.items()
                )
                for exclusion in exclusions
            )
        ]

    def register_sessions(
        self,
        project: Project,
        *,
        requires: list[str],
        default: bool = False,
    ) -> list[str]:
        """Register uv-isolated jobs and their aggregate compatibility session."""
        combinations = self.combinations(project)
        names = [self._session_name(combination) for combination in combinations]
        for name, combination in zip(names, combinations, strict=True):
            self._register_combination(project, name, combination, requires=requires)

        nox.session(
            name="compatibility",
            requires=names or requires,
            default=default,
            venv_backend="none",
        )(self._aggregate_session)
        return names

    @staticmethod
    def _session_name(combination: dict[str, str]) -> str:
        parts = ["compatibility"]
        if "python" in combination:
            parts.append(combination["python"])
        parts.extend(
            f"{name}-{combination[name]}"
            for name in sorted(combination)
            if name != "python"
        )
        return re.sub(r"[^A-Za-z0-9._-]+", "-", "-".join(parts)).strip("-")

    def _register_combination(
        self,
        project: Project,
        name: str,
        combination: dict[str, str],
        *,
        requires: list[str],
    ) -> None:
        python_version = combination.get("python")
        requested_packages = [
            f"{package}=={version}"
            for package, version in sorted(combination.items())
            if package != "python"
        ]

        def run_matrix(session: nox.Session) -> None:
            session.env.update(project.env)
            command = ["pytest", *project.args.get("pytest", [])]
            try:
                session.install("-e", ".", "pytest", *requested_packages)
                Reporter.run_command(session, name, command)
            except Exception as error:
                Reporter.record_failure(name, command, error)
                raise

        nox.session(
            name=name,
            python=python_version,
            venv_backend=self.environment_manager.select("matrix"),
            requires=requires or None,
            allow_parallel=True,
            default=False,
        )(run_matrix)

    @staticmethod
    def _aggregate_session(session: nox.Session) -> None:
        pass