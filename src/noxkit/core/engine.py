from inspect import getdoc
from pathlib import Path

import nox

from noxkit.core.reporting import Reporter
from noxkit.core.validation import validate_tool_installed
from noxkit.matrix.engine import MatrixEngine
from noxkit.project import Project
from noxkit.tools import Tool
from noxkit.tools.registry import tools

_REPORT_DIRECTORY_ENV = "NOXKIT_REPORT_DIRECTORY"


class NoxKitEngine:
    """Orchestrates the generation of Nox sessions."""

    def __init__(self, project: Project):
        self.project = project
        self.matrix_engine = MatrixEngine()

    def register_sessions(self) -> None:
        """Register Nox sessions for the configured project checks."""
        self.project.validate()

        configured_tools = [tool for stage in self.project.stages for tool in stage.tools]
        tool_names = [name for name in configured_tools if isinstance(name, str)]
        unknown_tools = [name for name in tool_names if name not in tools]
        if unknown_tools:
            available_tools = ", ".join(sorted(tools))
            raise ValueError(
                f"unknown tool(s): {', '.join(unknown_tools)}. "
                f"Available tools: {available_tools}"
            )

        resolved_tools = [
            tools[tool] if isinstance(tool, str) else tool
            for tool in configured_tools
        ]
        session_names = [tool.session_name for tool in resolved_tools]
        if len(session_names) != len(set(session_names)):
            raise ValueError("each pipeline tool must have a unique Nox session name")

        stage_names = [stage.name for stage in self.project.stages]
        pipeline_stage_names = [f"pipeline-{stage.name}" for stage in self.project.stages]
        all_session_names = [
            *session_names,
            *stage_names,
            *pipeline_stage_names,
            "pipeline",
            "check",
        ]
        if len(all_session_names) != len(set(all_session_names)):
            raise ValueError("tool, stage, and pipeline sessions must have unique names")

        previous_pipeline_stage: str | None = None
        for stage_index, stage in enumerate(self.project.stages):
            current_stage_sessions: list[str] = []
            for index, configured_tool in enumerate(stage.tools):
                requires: list[str] = []
                if not stage.parallel and index > 0:
                    requires = [current_stage_sessions[-1]]
                checker = (
                    tools[configured_tool]
                    if isinstance(configured_tool, str)
                    else configured_tool
                )
                self._register_tool(
                    checker,
                    requires=requires,
                    allow_parallel=stage.parallel,
                )
                current_stage_sessions.append(checker.session_name)

            stage_requires = (
                current_stage_sessions
                if stage.parallel
                else current_stage_sessions[-1:]
            )
            self._register_aggregate_session(
                stage.name,
                requires=stage_requires,
                description=f"Run the {stage.name} stage.",
                allow_parallel=stage.parallel,
            )

            pipeline_stage_name = pipeline_stage_names[stage_index]
            pipeline_requires = [stage.name]
            if previous_pipeline_stage is not None:
                pipeline_requires.insert(0, previous_pipeline_stage)
            self._register_aggregate_session(
                pipeline_stage_name,
                requires=pipeline_requires,
                description=f"Run pipeline through the {stage.name} stage.",
            )
            previous_pipeline_stage = pipeline_stage_name

        if previous_pipeline_stage is not None:
            self._register_aggregate_session(
                "pipeline",
                requires=[previous_pipeline_stage],
                description="Run the complete project pipeline.",
                default=True,
            )

        self._register_check_session()
        Reporter.register_final_summary(
            {
                (tool if isinstance(tool, str) else tool.session_name): stage.name
                for stage in self.project.stages
                for tool in stage.tools
            }
        )

    def _register_tool(
        self,
        checker: Tool,
        *,
        requires: list[str],
        allow_parallel: bool,
    ) -> None:
        args = self.project.args.get(checker.session_name, [])
        dependencies = self.project.dependencies.get(
            checker.session_name,
            list(checker.dependencies)
            or ([] if checker.dependency_group else [checker.session_name]),
        )

        def run_checker(session: nox.Session) -> None:
            session.install("-e", ".")
            if checker.dependency_group:
                session.install("--group", checker.dependency_group)
            if dependencies:
                session.install(*dependencies)
            validate_tool_installed(session, checker)
            Reporter.run_command(
                session,
                checker.session_name,
                checker.get_command(args),
            )

        description = checker.description
        if description is None and type(checker) is not Tool:
            description = getdoc(type(checker))
        run_checker.__doc__ = description or f"Run {checker.session_name}."
        nox.session(
            name=checker.session_name,
            requires=requires or None,
            allow_parallel=allow_parallel,
            default=False,
        )(run_checker)

    def _register_check_session(self) -> None:
        package_root = Path(__file__).resolve().parents[1]

        def check(session: nox.Session) -> None:
            self.project.validate()
            session.install("-e", ".")
            session.run("python", "-m", "compileall", "-q", str(package_root))
            session.run(
                "python",
                "-c",
                "from noxkit import NoxKitEngine, Project, Stage, Tool; "
                "Project().validate()",
            )

        check.__doc__ = "Validate the project configuration and NoxKit package."
        nox.session(name="check", default=False)(check)

    @staticmethod
    def _register_aggregate_session(
        name: str,
        *,
        requires: list[str],
        description: str,
        allow_parallel: bool = False,
        default: bool = False,
    ) -> None:
        def run_stage(session: nox.Session) -> None:
            pass

        run_stage.__doc__ = description
        nox.session(
            name=name,
            requires=requires,
            allow_parallel=allow_parallel,
            default=default,
        )(run_stage)
