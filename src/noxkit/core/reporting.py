import atexit
import hashlib
import json
import os
import re
import shlex
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import nox

_REPORT_DIRECTORY_ENV = "NOXKIT_REPORT_DIRECTORY"


@dataclass
class Reporter:
    """Collects and summarizes results from generated sessions."""

    results: list[dict[str, Any]] = field(default_factory=list)

    def add_result(self, result: dict[str, Any]) -> None:
        self.results.append(result)

    def render(self) -> str:
        """Render a stage-grouped run summary."""
        if not self.results:
            return ""

        stages: dict[str, list[dict[str, Any]]] = {}
        for result in self.results:
            stage = result.get("stage", "Jobs")
            stages.setdefault(stage, []).append(result)

        passed = sum(result.get("status") == "PASS" for result in self.results)
        failed = sum(result.get("status") == "FAIL" for result in self.results)
        skipped = sum(result.get("status") == "SKIP" for result in self.results)
        not_executed = sum(
            result.get("status") == "NOT RUN" for result in self.results
        )
        lines = ["NoxKit Summary", "--------------"]
        for stage, results in stages.items():
            name_width = max(len(result.get("name", "unknown")) for result in results)
            if any(result.get("status") == "FAIL" for result in results):
                heading = f"{stage} [FAIL]"
            elif any(result.get("status") == "NOT RUN" for result in results):
                heading = f"{stage} [INCOMPLETE]"
            else:
                heading = stage
            lines.extend(("", heading, "-" * len(heading)))
            for result in results:
                status = result.get("status", "UNKNOWN")
                name = result.get("name", "unknown")
                line = f"  [{status}]  {name:<{name_width}}"
                duration = result.get("duration")
                if isinstance(duration, (int, float)):
                    line += f"  {duration:.2f}s"
                coverage = result.get("coverage")
                if coverage is not None:
                    line += f"  Coverage: {coverage}%"
                lines.append(line)
                reason = result.get("reason")
                if reason:
                    lines.append(f"    Reason: {reason}")
                exit_code = result.get("exit_code")
                if exit_code is not None:
                    lines.append(f"    Exit code: {exit_code}")
                if status == "FAIL":
                    lines.append(f"    Rerun: {shlex.join(['nox', '--session', name])}")
        result_status = "FAIL" if failed else "INCOMPLETE" if not_executed else "PASS"
        lines.extend(
            (
                "",
                (
                    f"Overall: {result_status}  |  {passed} passed, "
                    f"{failed} failed, {skipped} skipped, "
                    f"{not_executed} not executed"
                ),
            )
        )
        return "\n".join(lines)

    @staticmethod
    def register_final_summary(stages_by_session: dict[str, str]) -> None:
        """Print one stage-grouped summary after Nox writes its final report."""
        if "--no-dependencies" in sys.argv or any(
            argument in {"-l", "--list", "--list-sessions", "--usage"}
            for argument in sys.argv
        ):
            return

        report_directory = Path(tempfile.mkdtemp(prefix="noxkit-report-"))
        os.environ[_REPORT_DIRECTORY_ENV] = str(report_directory)
        report_path = _report_path_from_args() or nox.options.report
        if report_path is None:
            report_path = report_directory / "results.json"
            nox.options.report = str(report_path)
        report_path = Path(report_path)

        def print_summary() -> None:
            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
                reporter = Reporter()
                for result in report.get("sessions", []):
                    name = result.get("name")
                    stage = stages_by_session.get(name)
                    if stage is None:
                        continue
                    coverage_path = report_directory / hashlib.sha256(
                        name.encode()
                    ).hexdigest()
                    try:
                        coverage = coverage_path.read_text(encoding="utf-8").strip()
                    except FileNotFoundError:
                        coverage = None
                    details_path = report_directory / (
                        "failure-" + hashlib.sha256(name.encode()).hexdigest()
                    )
                    try:
                        details = json.loads(details_path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError):
                        details = {}
                    status = str(result.get("result", "")).lower()
                    reporter.add_result(
                        {
                            "stage": stage,
                            "name": name,
                            "status": _display_status(status),
                            "duration": result.get("duration"),
                            "reason": result.get("reason") or details.get("reason"),
                            "exit_code": details.get("exit_code"),
                            "coverage": coverage or None,
                        }
                    )
                if reporter.results:
                    print(reporter.render())
            except (OSError, json.JSONDecodeError, TypeError, AttributeError) as error:
                print("NoxKit Summary")
                print("--------------")
                print(f"Overall: UNKNOWN  |  Unable to read Nox report: {error}")
            finally:
                shutil.rmtree(report_directory, ignore_errors=True)

        atexit.register(print_summary)

    @staticmethod
    def run_command(session: Any, name: str, command: list[str]) -> None:
        """Run a job and retain pytest-cov's total for the final summary."""
        if name != "pytest-cov":
            session.run(*command)
            return

        with tempfile.TemporaryFile(mode="w+t") as output_file:
            try:
                session.run(*command, stdout=output_file)
            finally:
                output_file.seek(0)
                output = output_file.read()
                print(output, end="")
                match = re.search(
                    r"^TOTAL\b.*?(\d+(?:\.\d+)?)%",
                    output,
                    re.MULTILINE,
                )
                report_directory = os.environ.get(_REPORT_DIRECTORY_ENV)
                if match and report_directory is not None:
                    coverage_path = Path(report_directory) / hashlib.sha256(
                        name.encode()
                    ).hexdigest()
                    coverage_path.write_text(match.group(1), encoding="utf-8")

    @staticmethod
    def record_failure(name: str, command: list[str], error: Exception) -> None:
        """Retain command details that Nox's JSON report does not include."""
        report_directory = os.environ.get(_REPORT_DIRECTORY_ENV)
        if report_directory is None:
            return
        details: dict[str, Any] = {
            "command": command,
            "reason": str(error) or type(error).__name__,
        }
        exit_code = getattr(error, "returncode", None)
        if isinstance(exit_code, int):
            details["exit_code"] = exit_code
        else:
            match = re.search(
                r"(?:exit|return(?:ed)?) code\s+(\d+)",
                str(error),
                re.IGNORECASE,
            )
            if match:
                details["exit_code"] = int(match.group(1))
        details_path = Path(report_directory) / (
            "failure-" + hashlib.sha256(name.encode()).hexdigest()
        )
        details_path.write_text(json.dumps(details), encoding="utf-8")


def _report_path_from_args() -> str | None:
    for index, argument in enumerate(sys.argv):
        if argument.startswith("--report="):
            return argument.partition("=")[2]
        if argument == "--report" and index + 1 < len(sys.argv):
            return sys.argv[index + 1]
    return None


def _display_status(result: str) -> str:
    if result in {"success", "passed", "pass"}:
        return "PASS"
    if result in {"failed", "failure", "error", "fail"}:
        return "FAIL"
    if result in {"skipped", "skip"}:
        return "SKIP"
    return "NOT RUN"