# NoxKit — Project Requirements

**Status:** Initial requirements draft  
**Project type:** Python package  
**Execution engine:** Nox  
**Matrix environment backend:** uv  
**Configuration style:** Declarative Python configuration

---

# 1. Project Overview

## 1.1 Purpose

NoxKit is an opinionated configuration and orchestration framework built on top of Nox.

Its purpose is to eliminate repetitive Nox configuration while providing a consistent, reusable approach to Python project validation.

A developer should be able to configure common linting, testing, coverage, and compatibility checks using a single configuration object rather than implementing individual Nox sessions for every project.

NoxKit must preserve the flexibility of Nox. Developers must be able to override predefined behavior and define ordinary custom Nox sessions alongside NoxKit-generated sessions.

## 1.2 Design Principles

1. **Nox is the execution engine.** NoxKit must not reinvent virtual environment or session management.
2. **Convention over configuration.** Common projects should require minimal configuration.
3. **Declarative configuration.** Developers describe what they want executed rather than implementing individual sessions.
4. **Everything is overridable.** Defaults should not restrict advanced use cases.
5. **Parallel by default.** Independent jobs should execute concurrently where possible.
6. **Incremental adoption.** NoxKit must coexist with existing Noxfiles and custom sessions.
7. **Minimal dependencies.** The core package should remain lightweight.
8. **Predictable behavior.** Configuration should be validated before execution.

## 1.3 Non-Goals

NoxKit is not intended to:

- Replace Nox.
- Replace uv, Poetry, pip, or other package managers.
- Implement its own virtual environment manager.
- Replace pytest or coverage.py.
- Become a general-purpose task runner.
- Require developers to use a particular project manager.
- Require lockfiles for compatibility testing.
- Provide an exhaustive catalog of every possible linting tool.

---

# 2. Configuration

## 2.1 Primary Configuration Object

NoxKit must expose a single primary configuration object.

The configuration object should describe:

- Python versions.
- Linting tools.
- Test execution.
- Coverage.
- Compatibility matrices.
- Execution stages.
- Environment configuration.
- Dependency configuration.
- Customization and overrides.

The configuration object should use sensible defaults and require minimal configuration for ordinary projects.

Illustrative API (not finalized):

```python
from noxkit import Project, Stage

project = Project(
    python=["3.12", "3.13", "3.14", "3.15"],
  stages=[
    Stage(name="lint", tools=["ruff"], parallel=True),
    Stage(name="tests", tools=["pytest"], parallel=False),
    Stage(name="coverage", tools=["pytest-cov"], parallel=False),
  ],
    compatibility={
        "django": "lts",
    },
)
```

## 2.2 Configuration Requirements

- Configuration must be expressed using ordinary Python objects.
- Configuration must be validated before executing jobs.
- Invalid or contradictory configuration must produce useful errors.
- Optional fields must have sensible defaults.
- Individual predefined checks must be independently configurable.
- Configuration must support tool-specific arguments and environment variables.
- Developers must be able to override default dependencies and execution behavior.
- Configuration must support custom jobs and execution stages.

## 2.3 Default Configuration

Proposed defaults:

| Feature | Default |
|---|---|
| Linter | Ruff |
| Tests | pytest |
| Coverage | coverage.py, if enabled |
| Python | Current project interpreter |
| Matrix | Disabled |
| Matrix environment | uv |
| Matrix dependency policy | Minimum supported versions |
| Execution | Parallel where independent |
| Reporting | Always |
| Environment reuse | Nox defaults |

---

# 3. Optional Dependencies and Installation

## 3.1 Core Installation

NoxKit must have minimal core dependencies.

Core functionality must not require installation of every supported checker.

## 3.2 Optional Dependency Groups

NoxKit must provide installation extras for predefined checkers.

Proposed extras:

| Extra | Dependencies |
|---|---|
| `lint` | Ruff, Pylint |
| `security` | Bandit |
| `testing` | pytest, coverage |
| `checks` | All predefined checkers |

Individual checkers should also be installable independently where practical.

Example:

```bash
pip install noxkit[checks]
```

The installation of an optional checker must not automatically enable it.

Configuration determines which checks execute.

---

# 4. Environment and Package Manager Integration

## 4.1 Supported Environments

NoxKit must work with Nox installed through:

- System Python / pip.
- uv.
- Poetry.
- Existing virtual environments.
- Other supported Nox installation methods.

NoxKit must not require a specific installation method.

## 4.2 Existing Project Environment

Normal project checks must use the project's existing development environment.

Examples:

| Project configuration | Expected behavior |
|---|---|
| Poetry | Run tests in the Poetry environment |
| uv | Run tests in the existing uv environment |
| pip / venv | Use the existing environment |
| System Python | Use the configured interpreter |

NoxKit must not unnecessarily recreate or replace the project's normal development environment.

## 4.3 Dependency Ownership

| Dependency | Environment |
|---|---|
| NoxKit | Nox execution environment |
| Predefined checkers | Project development environment |
| Normal pytest | Project development environment |
| Normal coverage.py | Project development environment |
| Matrix dependencies | Isolated uv environments |

## 4.4 Environment Backend

NoxKit must leverage Nox's existing virtual environment backends.

uv should be the preferred backend for matrix environments.

Poetry integration should primarily concern executing normal checks in the existing Poetry environment, not implementing a separate Poetry environment manager.

## 4.5 Noxfile and Runner Installation

Nox imports `noxfile.py` using the Python environment that launches Nox. Imports
in the Noxfile are evaluated before any Nox session starts, so installing
NoxKit with `session.install()` is too late. NoxKit must be installed and
importable in the same environment as the Nox command that loads the Noxfile.

For Python projects, Nox and NoxKit should be installed as development or tool
dependencies in the environment used to invoke Nox.

Non-Python projects do not need to create a Python package or project virtual
environment to use NoxKit. They can install Nox and NoxKit in a dedicated tool
environment, for example:

```bash
uv tool install nox --with noxkit
```

For development from a local NoxKit checkout, the tool environment may use an
editable install:

```bash
uv tool install nox --with-editable /path/to/NoxKit
```

The `nox` command on `PATH` must resolve to the environment containing NoxKit.
NoxKit sessions may then run project commands such as `npm`, `cargo`, or
`make`; they must not assume the target repository is itself a Python package.

---

# 5. Predefined Static Analysis

## 5.1 Supported Checkers

Initial supported checkers:

| Checker | Purpose |
|---|---|
| Ruff | Linting and formatting validation |
| Pylint | Static analysis |
| Bandit | Security analysis |
| Mypy | Static typing |
| Pyright | Static typing |

Additional checkers may be added later.

## 5.2 Requirements

- Each checker must be independently enabled or disabled.
- Each checker must support custom command-line arguments.
- Each checker must support tool-specific configuration.
- Each checker must report an independent execution result.
- Checker failures must not automatically prevent unrelated checks from executing.
- Checkers should share environments where appropriate.
- Developers must be able to register custom checkers.

## 5.3 Individual Invocation

Every predefined checker must be independently invocable through Nox.

Examples:

```bash
nox --session ruff
nox --session pylint
nox --session bandit
```

The actual session names should be documented and discoverable.

---

# 6. Testing and Coverage

## 6.1 Pytest

NoxKit must provide predefined pytest execution.

Requirements:

- Execute pytest in the existing project environment.
- Support custom pytest arguments.
- Respect existing pytest configuration.
- Capture test counts, failures, errors, and skipped tests.
- Preserve pytest exit status.
- Support independent invocation.

Example:

```bash
nox --session tests
```

## 6.2 Coverage

Coverage must use the version installed in the project's existing environment.

NoxKit must not install or upgrade coverage.py simply to satisfy its own dependency requirements.

Requirements:

- Support coverage.py.
- Support configured coverage thresholds.
- Capture total coverage percentage.
- Capture coverage failures.
- Support terminal reporting.
- Support machine-readable reporting where practical.
- Include coverage results in the final summary.

Coverage must be independently invocable if enabled.

Matrix testing should not automatically introduce a different coverage version or alter the project's pinned coverage dependency.

Matrix coverage collection and aggregation should be optional future functionality.

---

# 7. Compatibility Matrix Engine

This is a core feature of NoxKit.

## 7.1 General Requirements

The matrix engine must be generic and support an arbitrary number of dimensions.

Examples:

- Python × Django.
- Python × Django × PostgreSQL.
- Python × Django × PostgreSQL × dependency version.

There must not be a hardcoded limit of two or three dimensions.

The engine must:

1. Accept multiple independent matrix dimensions.
2. Generate the Cartesian product of configured dimensions.
3. Apply compatibility constraints.
4. Apply explicit inclusion and exclusion rules.
5. Generate individual Nox sessions for valid combinations.
6. Execute combinations in isolated uv environments.
7. Report each combination independently.

Large matrices must be supported, although developers should be encouraged to limit unnecessary combinations.

## 7.2 Version Discovery

NoxKit should provide convenient version discovery using Trove classifiers where available.

Examples:

```python
compatibility={
    "python": "supported",
    "django": "lts",
}
```

Supported discovery selectors should include:

- `supported`: Versions declared as supported by the relevant package metadata.
- `lts`: LTS versions where the ecosystem provides that classification.
- Explicit version lists.

Trove classifiers should be the quick and easy discovery mechanism, not a mandatory source of truth.

## 7.3 Explicit Version Configuration

Developers must be able to explicitly specify versions.

Example:

```python
compatibility={
    "python": ["3.12", "3.13", "3.14", "3.15"],
    "django": ["4.2", "5.2", "6.0"],
}
```

Explicit version configuration must take precedence over automatic discovery for that dimension.

The engine should also support explicit inclusion and exclusion of versions when automatic discovery is being used.

## 7.4 Compatibility Providers

The matrix engine must be independent of individual framework implementations.

Framework-specific providers supply:

- Version discovery.
- Version classification.
- Compatibility rules.
- Optional release metadata.
- Default dependency requirements.

Django must be supported out of the box.

Additional providers may be implemented in the future.

Django-specific requirements:

- Discover supported Django versions.
- Identify Django LTS releases.
- Determine compatible Python versions.
- Exclude incompatible combinations.
- Allow developers to override provider decisions.

LTS classification must not rely exclusively on Trove classifiers. Where metadata does not provide the necessary information, NoxKit must use provider-maintained metadata or explicit configuration.

## 7.5 Excluding Matrix Combinations

Developers must be able to explicitly exclude individual combinations.

Example:

```python
compatibility={
    "python": ["3.12", "3.13", "3.14"],
    "django": ["4.2", "5.2", "6.0"],

    "exclude": [
        {"python": "3.14", "django": "4.2"},
        {"python": "3.12", "django": "6.0"},
    ],
}
```

The engine must also support custom skip predicates for more complex rules.

Example:

```python
def skip_combination(combo):
    return (
        combo["python"] == "3.14"
        and combo["django"] == "4.2"
    )
```

Requirements:

- Exact combination exclusions.
- Custom predicate-based exclusions.
- Compatibility-provider exclusions.
- Explicit inclusion overrides where appropriate.
- Clear precedence rules for conflicting configuration.
- A reason must be associated with every skipped combination.
- Skipped combinations must appear in the final report.

Example skip output:

```text
[SKIP] Python 3.14 / Django 4.2
       Reason: Django 4.2 does not support Python 3.14.
```

The exclusion mechanism must work with any number of dimensions.

## 7.6 Matrix Environment Creation

Matrix sessions must use isolated uv environments through Nox's uv backend.

Requirements:

- Automatically obtain or locate the requested Python interpreter.
- Create isolated environments.
- Install the project under test.
- Install the requested framework and dependency versions.
- Install required test dependencies.
- Execute pytest.
- Capture results independently.
- Avoid requiring generated lockfiles.
- Avoid modifying the project's normal environment.

## 7.7 Matrix Dependency Policies

Support dependency version policies:

| Policy | Behavior |
|---|---|
| `minimum` | Install minimum supported versions |
| `latest` | Install latest compatible versions |
| `pinned` | Use explicitly configured versions |
| `project` | Use the existing project environment |

`minimum` should be the default for compatibility matrix testing.

The policy must apply independently to matrix dimensions and supporting dependencies where appropriate.

## 7.8 Matrix Invocation

The entire compatibility matrix must be independently invocable.

Example:

```bash
nox --session compatibility
```

Individual combinations should ideally be independently addressable for troubleshooting.

Example (exact naming TBD):

```bash
nox --session compatibility-3.12-django-4.2
```

---

# 8. Execution and Orchestration

## 8.1 Execution Stages

NoxKit must support configurable execution stages.

Each stage must support:

- Synchronous execution.
- Asynchronous/parallel execution.
- Dependencies on other stages.
- Custom jobs.
- Failure policies.

Default behavior should maximize parallel execution.

## 8.2 Execution Rules

- Stages execute in declared order unless explicitly configured otherwise.
- Independent jobs within parallel stages execute concurrently.
- Jobs in synchronous stages execute sequentially.
- Independent failures must not unnecessarily prevent other jobs from running.
- Dependent stages may be skipped when prerequisites fail.
- Final reporting must execute regardless of ordinary job failures.
- Maximum concurrency must be configurable.

Nox's existing parallel execution facilities should be leveraged wherever possible.

## 8.3 Custom Jobs

Developers must be able to define ordinary Nox sessions.

Example:

```python
import nox

@nox.session
def build_docs(session):
    session.install("mkdocs")
    session.run("mkdocs", "build")
```

Custom sessions must coexist with NoxKit-generated sessions.

Custom jobs should eventually be eligible for registration in NoxKit execution stages.

---

# 9. Reporting

Reporting is a major differentiating feature.

## 9.1 Final Summary

Every full NoxKit run must generate a consolidated summary.

The report must include:

- Overall execution status.
- Number of successful jobs.
- Number of failed jobs.
- Number of skipped jobs.
- Individual checker results.
- Test results.
- Matrix combination results.
- Coverage percentage.
- Coverage threshold status.
- Failure reasons.

## 9.2 Actionable Failure Reporting

When a job fails during a full run, the summary must display the individual command needed to rerun that job.

Example:

```text
NoxKit Results
==============

Static Analysis
  [PASS] Ruff
  [FAIL] Pylint
  [PASS] Bandit

Testing
  [PASS] Pytest

Compatibility Matrix
  [PASS] Python 3.12 / Django 4.2
  [FAIL] Python 3.13 / Django 5.2
  [PASS] Python 3.14 / Django 5.2

Coverage
  Total:      87.4%
  Threshold:  85.0%
  Status:     PASS

Summary
-------
Passed:   5
Failed:   2
Skipped:  0

Overall: FAILED

To investigate failures, run:

  nox --session pylint
  nox --session compatibility-3.13-django-5.2
```

The exact session invocation must be generated from the actual registered session names.

## 9.3 Individual Session Results

When a developer invokes an individual session, it should still produce useful output for that session.

Example:

```bash
nox --session ruff
```

Should display the checker result without requiring a complete NoxKit run.

## 9.4 Report Session

Provide an independently invocable reporting session.

Example:

```bash
nox --session report
```

This should display the results of the most recent available run.

The implementation must define where and how previous run results are stored.

## 9.5 Output Formats

Initial requirements:

- Human-readable terminal output.
- Clear success/failure indicators.
- Useful error messages.
- Optional JSON reporting.
- Optional JUnit XML integration.

Normal Nox output must remain visible.

---

# 10. Extensibility

NoxKit must support two levels of customization.

## 10.1 Predefined Job Overrides

Developers must be able to override:

- Command-line arguments.
- Dependencies.
- Environment variables.
- Python versions.
- Working directories.
- Execution stages.
- Failure behavior.
- Tool-specific configuration.

## 10.2 Custom Integrations

The architecture should allow additional checker and matrix providers without modifying the core implementation.

Initial extensibility targets:

- Additional linting tools.
- Additional security tools.
- Additional testing frameworks.
- Additional framework compatibility providers.

Django is the initial built-in matrix provider.

---

# 11. Nonfunctional Requirements

## 11.1 Performance

- Independent jobs should execute concurrently by default.
- Matrix generation should be efficient.
- Matrix environments should be reusable where appropriate.
- Version discovery should be cached.
- Concurrency should be configurable.

## 11.2 Reliability

- A single job failure must not prevent unrelated jobs from completing.
- Final reporting must run after failures.
- Results must accurately reflect actual execution status.
- Interrupted executions should not be reported as successful.
- Missing interpreters and unavailable dependencies must produce useful errors.

## 11.3 Compatibility

- Support currently maintained Python versions.
- Work with common Nox installation methods.
- Work with Poetry, uv, pip, and existing virtual environments.
- Support ordinary custom Nox sessions.
- Avoid imposing a specific project structure.

## 11.4 Maintainability

- Prefer small, focused modules.
- Keep the matrix engine generic.
- Avoid unnecessary abstractions.
- Keep tool integrations independent.
- Use type annotations.
- Provide comprehensive automated tests.
- Maintain a documented public API.

---

# 12. MVP Scope

The initial release should focus on the following:

| Feature | Priority |
|---|---|
| Single configuration object | Required |
| Nox integration | Required |
| Ruff | Required |
| Pylint | Required |
| Bandit | Required |
| Pytest | Required |
| Existing environment execution | Required |
| Coverage reporting | Required |
| Generic multidimensional matrix | Required |
| Explicit matrix versions | Required |
| Trove-based discovery | Required |
| Django provider | Required |
| Exact combination exclusions | Required |
| Custom skip predicates | Required |
| uv matrix environments | Required |
| Minimum dependency policy | Required |
| Parallel execution | Required |
| Synchronous stages | Required |
| Individual session invocation | Required |
| Final summary | Required |
| Actionable rerun instructions | Required |
| Custom Nox sessions | Required |
| JSON reporting | Later |
| Additional framework providers | Later |
| Advanced custom scheduling | Later |
| Matrix coverage aggregation | Later |

---

# 13. Implementation Task Breakdown

The project should be developed in small, independently testable increments.

Each task should leave the project in a working state.

## Phase 1 — Project Foundation

- [ ] Create the Python package repository.
- [ ] Configure `pyproject.toml`.
- [ ] Configure build backend.
- [ ] Configure Ruff.
- [ ] Configure pytest.
- [ ] Configure type checking.
- [ ] Configure package testing and CI.
- [ ] Create the initial package structure.
- [ ] Establish supported Python versions.
- [ ] Add a minimal Noxfile for developing NoxKit itself.

**Deliverable:** Installable package with automated tests and development tooling.

## Phase 2 — Configuration Model

- [ ] Define the primary `Project` configuration object.
- [ ] Define configuration models for linting.
- [ ] Define configuration models for testing.
- [ ] Define configuration models for coverage.
- [ ] Define configuration models for matrix testing.
- [ ] Define configuration models for execution stages.
- [ ] Define configuration models for dependencies.
- [ ] Implement default configuration behavior.
- [ ] Implement configuration validation.
- [ ] Write configuration unit tests.
- [ ] Document the initial public API.

**Deliverable:** A fully validated configuration object without execution functionality.

## Phase 3 — Nox Integration

- [ ] Investigate Nox session generation and registration.
- [ ] Investigate Nox session parameterization.
- [ ] Implement Noxfile integration.
- [ ] Generate a basic NoxKit session.
- [ ] Generate independently invocable sessions.
- [ ] Verify custom Nox sessions coexist with generated sessions.
- [ ] Test Nox invocation with different installation methods.
- [ ] Verify configuration is available to the Nox execution interpreter.

**Deliverable:** NoxKit can register generated sessions and coexist with normal Noxfiles.

## Phase 4 — Static Analysis

- [ ] Implement a generic checker interface.
- [ ] Implement Ruff integration.
- [ ] Implement Pylint integration.
- [ ] Implement Bandit integration.
- [ ] Support checker arguments.
- [ ] Support checker-specific configuration.
- [ ] Capture checker exit status.
- [ ] Capture execution output.
- [ ] Implement individual checker sessions.
- [ ] Add optional dependency groups.
- [ ] Add checker integration tests.

**Deliverable:** Independently executable predefined static analysis sessions.

## Phase 5 — Testing and Coverage

- [ ] Implement pytest integration.
- [ ] Detect or configure the project environment.
- [ ] Implement Poetry environment execution.
- [ ] Implement uv environment execution.
- [ ] Support ordinary virtualenv/system environments.
- [ ] Capture pytest results.
- [ ] Implement coverage reporting.
- [ ] Capture coverage percentage.
- [ ] Implement coverage thresholds.
- [ ] Preserve project-pinned coverage dependencies.
- [ ] Add integration tests.

**Deliverable:** Normal project tests and coverage execute without modifying the project's environment.

## Phase 6 — Generic Matrix Engine

- [ ] Define a generic matrix dimension model.
- [ ] Support arbitrary numbers of dimensions.
- [ ] Implement Cartesian product generation.
- [ ] Implement explicit version lists.
- [ ] Implement automatic version discovery.
- [ ] Implement Trove classifier parsing.
- [ ] Implement explicit version inclusion.
- [ ] Implement exact combination exclusions.
- [ ] Implement predicate-based exclusions.
- [ ] Implement compatibility constraints.
- [ ] Implement skip reasons.
- [ ] Define inclusion/exclusion precedence.
- [ ] Add extensive matrix unit tests.

**Deliverable:** Generic matrix generation independent of Nox, uv, and framework-specific providers.

## Phase 7 — Django Provider

- [ ] Define the matrix provider interface.
- [ ] Implement Django version discovery.
- [ ] Implement Django LTS metadata.
- [ ] Implement Django/Python compatibility rules.
- [ ] Implement Django version selectors.
- [ ] Add provider override support.
- [ ] Test known compatible and incompatible combinations.
- [ ] Document Django matrix configuration.

**Deliverable:** Django compatibility matrices generated automatically.

## Phase 8 — uv Matrix Execution

- [ ] Investigate Nox uv backend behavior.
- [ ] Configure isolated matrix environments.
- [ ] Implement Python interpreter selection.
- [ ] Verify automatic Python installation behavior.
- [ ] Implement project installation.
- [ ] Implement framework dependency installation.
- [ ] Implement minimum dependency policies.
- [ ] Implement latest dependency policies.
- [ ] Implement explicit pinned dependencies.
- [ ] Execute pytest in matrix environments.
- [ ] Capture individual matrix results.
- [ ] Verify no project environment modifications.
- [ ] Test environment reuse.

**Deliverable:** Actual compatibility testing across isolated uv environments.

## Phase 9 — Execution Orchestration

- [ ] Define job result models.
- [ ] Define stage models.
- [ ] Implement synchronous stages.
- [ ] Implement parallel stages.
- [ ] Implement stage dependencies.
- [ ] Implement configurable concurrency.
- [ ] Implement failure continuation behavior.
- [ ] Ensure finalization after failures.
- [ ] Integrate custom jobs.
- [ ] Test parallel execution and failure scenarios.

**Deliverable:** Full NoxKit execution pipeline.

## Phase 10 — Reporting

- [ ] Implement result aggregation.
- [ ] Implement terminal summary.
- [ ] Display individual checker results.
- [ ] Display matrix results.
- [ ] Display skipped combinations and reasons.
- [ ] Display coverage results.
- [ ] Generate individual rerun commands.
- [ ] Implement persistent run result storage.
- [ ] Implement independent report session.
- [ ] Implement overall exit status.
- [ ] Add reporting tests.

**Deliverable:** Actionable final report after every full run.

## Phase 11 — Documentation and Release

- [ ] Write installation documentation.
- [ ] Write configuration reference.
- [ ] Document supported checkers.
- [ ] Document environment behavior.
- [ ] Document matrix configuration.
- [ ] Document Django support.
- [ ] Document custom Nox sessions.
- [ ] Add complete example project.
- [ ] Add troubleshooting guide.
- [ ] Verify package builds and installs.
- [ ] Publish initial release.

**Deliverable:** Usable, documented MVP.

---

# 14. Architectural Questions Requiring Investigation

These are implementation questions rather than blockers to the requirements.

1. How can NoxKit reliably register dynamically generated sessions while preserving ordinary Nox session behavior?
2. How should a final report session be guaranteed to execute after parallel session failures?
3. What is the best mechanism for collecting results across Nox worker processes?
4. How should individual matrix combinations be named and selected?
5. How should NoxKit persist the last run's results?
6. How should environment reuse interact with changing matrix dependency policies?
7. How should the package handle version discovery when PyPI or network access is unavailable?
8. How should custom inclusion rules interact with provider compatibility exclusions?

These should be investigated with small prototypes before committing to implementation details.

---

# 15. Definition of Success

A developer should be able to add NoxKit to an existing Python project, define a small configuration object, and immediately gain:

- Standardized static analysis.
- Normal project-environment testing.
- Coverage reporting.
- Multidimensional compatibility testing.
- Isolated uv matrix environments.
- Parallel execution.
- Independent job invocation.
- Useful failure summaries.
- Full compatibility with custom Nox sessions.

The ultimate goal is to provide a complete, opinionated Python validation setup with minimal configuration and without sacrificing the flexibility of Nox.