import atexit
import hashlib
import json
import os
import re
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
        failed = len(self.results) - passed
        lines = ["NoxKit Summary", "--------------"]
        for stage, results in stages.items():
            name_width = max(len(result.get("name", "unknown")) for result in results)
            lines.extend(("", stage, "-" * len(stage)))
            for result in results:
                status = result.get("status", "UNKNOWN")
                name = result.get("name", "unknown")
                line = f"  [{status}]  {name:<{name_width}}"
                coverage = result.get("coverage")
                if coverage is not None:
                    line += f"  Coverage: {coverage}%"
                else:
                    line = line.rstrip()
                lines.append(line)
        result_status = "PASS" if failed == 0 else "FAIL"
        lines.extend(
            (
                "",
                f"Overall: {result_status}  |  {passed} passed, {failed} failed",
            )
        )
        return "\n".join(lines)

    @staticmethod
    def register_final_summary(stages_by_session: dict[str, str]) -> None:
        """Print one stage-grouped summary after Nox writes its final report."""
        if "--no-dependencies" in sys.argv:
            return

        report_directory = Path(tempfile.mkdtemp(prefix="noxkit-report-"))
        os.environ[_REPORT_DIRECTORY_ENV] = str(report_directory)
        report_path = _report_path_from_args() or nox.options.report
        if report_path is None:
            report_path = report_directory / "results.json"
            nox.options.report = str(report_path)

        def print_summary() -> None:
            try:
                report = json.loads(Path(report_path).read_text(encoding="utf-8"))
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
                    reporter.add_result(
                        {
                            "stage": stage,
                            "name": name,
                            "status": (
                                "PASS" if result.get("result") == "success" else "FAIL"
                            ),
                            "coverage": coverage or None,
                        }
                    )
                if reporter.results:
                    print(reporter.render())
            except (OSError, json.JSONDecodeError):
                pass
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


def _report_path_from_args() -> str | None:
    for index, argument in enumerate(sys.argv):
        if argument.startswith("--report="):
            return argument.partition("=")[2]
        if argument == "--report" and index + 1 < len(sys.argv):
            return sys.argv[index + 1]
    return None