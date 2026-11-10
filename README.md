# NoxKit

NoxKit turns a `Project` configuration into Nox sessions. Define ordered stages
in `noxfile.py`, then register them with `NoxKitEngine`:

```python
import nox

from noxkit import NoxKitEngine, Project, Stage, Tool

nox.options.default_venv_backend = "uv|virtualenv"

project = Project(
	stages=[
		Stage(name="lint", tools=["ruff", "bandit"], parallel=True),
		Stage(
			name="type-check",
			tools=[Tool("ty", command_prefix=("ty", "check"))],
		),
		Stage(
			name="format-check",
			tools=[
				Tool(
					"black",
					default_args=("--check", "."),
				)
			],
		),
	],
)
NoxKitEngine(project).register_sessions()
```

When using NoxKit from a source checkout with a `src/` layout, add that source
directory to `sys.path` before importing `noxkit`, as the repository's own
`noxfile.py` does. NoxKit must also be importable by the Python environment that
launches Nox, because Nox imports the Noxfile before starting a session.

Normal checker sessions use Nox's `none` backend and do not install packages.
Launch Nox from the project's development environment so its executables are on
`PATH`, for example `uv run nox`, `poetry run nox`, or `nox` from an activated
virtual environment. Nox and NoxKit must be installed in, or otherwise
importable by, the environment that runs the Nox command.

## Stages and Tools

Each `Stage` has a name, an ordered list of tools, and a `parallel` flag. A tool
can be a string from the built-in registry or an inline `Tool` instance for a
tool that is not registered:

```python
Stage(
	name="lint",
	tools=["ruff", Tool("flake8")],
	parallel=True,
)
```

The built-in registry currently includes `ruff`, `ruff-format`, `pylint`,
`bandit`, `pytest`, `pytest-cov`, `mypy`, and `pyright`. For inline tools, the
session name is also the default executable name. Set `command_prefix` when the
command differs and `default_args` for default command-line arguments. Normal
checks use tools already installed in the project's development environment;
matrix package versions are configured with `Project.compatibility`.

## Normal Checks and Matrix Runs

Normal tool sessions neither create a virtual environment nor install or update
dependencies. Install checkers in the project's existing development
environment and configure any required environment variables with `Project.env`.
Non-empty `Tool.dependencies`, `Tool.dependency_group`, or
`Project.dependencies` entries are rejected for normal checks; NoxKit will not
silently install them.

Compatibility matrices use isolated uv-backed Nox sessions. Configure explicit
version lists; each matrix job installs the project, `pytest`, and each requested
package version without generating a lockfile:

```python
project = Project(
	python=["3.12", "3.13"],
	compatibility={"django": ["4.2", "5.0"]},
)
```

Run the aggregate with `nox --session compatibility`, or a single generated job
such as `nox --session compatibility-3.12-django-4.2`. `Project.exclude` and
`Project.skip_combination` filter combinations before sessions are registered.
`Project.args["pytest"]` supplies arguments to matrix test runs.

`Project.args` supplies additional command-line arguments keyed by tool session
name for normal checks.

## Running Sessions

NoxKit registers a session for every tool and an aggregate session for every
stage. Run a whole stage without invoking earlier stages, or run the ordered
pipeline:

```sh
nox -s lint
nox -s type-check
nox -s ruff
nox -s pipeline
```

`nox -s type-check` runs only tools in the `type-check` stage. `nox -s ruff`
runs only Ruff. `nox -s pipeline` runs all configured stages in order; use
`nox -p -s pipeline` to allow tools in parallel stages to run concurrently.

The repository's own `check` session is an opt-in local smoke test for NoxKit's
imports and source compilation. It is separate from the configured project
pipeline and can be run with `nox -s check`.

## Project API

`Project` is the top-level configuration object:

```python
Project(
	python=[],
	compatibility={},
	args={},
	env={},
	exclude=[],
	skip_combination=None,
	dependencies={},
	stages=[],
	max_concurrency=None,
)
```

| Field | Type | Current behavior |
|---|---|---|
| `python` | `list[str]` | Adds requested Python versions to the compatibility matrix. |
| `compatibility` | `dict[str, Any]` | Maps package names to explicit version lists for the compatibility matrix. |
| `args` | `dict[str, list[str]]` | Adds arguments to a tool command, keyed by its Nox session name. |
| `env` | `dict[str, str]` | Environment variables applied to normal and matrix commands. |
| `exclude` | `list[dict[str, Any]]` | Excludes matrix combinations matching each partial mapping. |
| `skip_combination` | `Callable[[dict[str, Any]], bool] \| None` | Filters matrix combinations before session registration. |
| `dependencies` | `dict[str, list[str]]` | Non-empty normal-check entries are rejected; normal sessions never install dependencies. |
| `stages` | `list[Stage]` | Defines the ordered pipeline and aggregate stage sessions. |
| `max_concurrency` | `int \| None` | A positive value is validated, but the limit is not yet applied to Nox execution. |

`Project.validate()` checks the supported configuration constraints and is called
automatically by `NoxKitEngine.register_sessions()`. Registration also rejects
unknown registry names and duplicate tool or Nox session names.

### Stage

`Stage(name, tools, parallel=True)` defines one aggregate Nox session. `name`
must be unique and must not collide with a tool session name. `tools` must be a
non-empty list of registered names or `Tool` instances, and a session may only
appear once in the pipeline.

With `parallel=True`, tools are eligible to run concurrently when Nox is invoked
with `-p`. With `parallel=False`, the tools run sequentially in list order. Stage
order is used by the `pipeline` session; selecting a stage directly does not run
earlier stages.

### Tool

`Tool` configures one Nox session:

```python
Tool(
	session_name,
	command_prefix=None,
	dependencies=(),
	default_args=(),
	description=None,
	dependency_group=None,
)
```

| Option | Behavior |
|---|---|
| `session_name` | Required for an inline tool. It names the Nox session and, by default, the executable to run. |
| `command_prefix` | Replaces the default executable command. |
| `default_args` | Arguments appended after `command_prefix` and before any `Project.args` for the session. |
| `dependencies` | Unsupported for normal checks; install checker dependencies in the development environment. Matrix pins use `Project.compatibility`. |
| `description` | Description shown by Nox when listing sessions. |
| `dependency_group` | Unsupported for normal checks; configure that dependency group in the development environment. |

Normal tool sessions execute the configured command directly in the environment
used to launch Nox. Matrix sessions alone create uv environments and install
their declared packages.

`Tool.get_command(args)` builds the final executable command as:

```text
command_prefix or (session_name,), default_args, args
```

Nox reports a missing executable as a failed session.

## Built-in Tool Names

The registry provides these names for use in `Stage.tools`:

| Name | Command |
|---|---|
| `ruff` | `ruff check` |
| `ruff-format` | `ruff format` |
| `pylint` | `pylint` |
| `bandit` | `bandit -r src` |
| `pytest` | `pytest` |
| `pytest-cov` | `pytest --cov` |
| `mypy` | `mypy` |
| `pyright` | `pyright` |

Any other executable can be configured inline with `Tool`, as in
`Tool("flake8")` or `Tool("ty", command_prefix=("ty", "check"))`.
