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
					dependency_group="format",
				)
			],
		),
	],
)
NoxKitEngine(project).register_sessions()
```

When using NoxKit from a source checkout with a `src/` layout, add that source
directory to `sys.path` before importing `noxkit`, as the repository's own
`noxfile.py` does. Installed projects do not need that bootstrap.

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
command differs, `default_args` for default command-line arguments, and
`dependencies` for extra packages to install.

## Tool Dependencies

Each tool session installs the project (`-e .`) into its isolated Nox
environment. To use a tool version selected by the project, declare it in a
dependency group and reference that group with `dependency_group`:

```toml
[dependency-groups]
format = ["black==24.10.0"]
```

```python
Tool("black", default_args=("--check", "."), dependency_group="format")
```

The group is installed with `uv`; NoxKit does not add an unpinned Black
requirement in this case. Alternatively, `Project.dependencies` can provide
per-session package requirements, keyed by session name. `Project.args` provides
additional command-line arguments keyed the same way.

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
| `python` | `list[str]` | Validates non-empty version strings. It does not yet create Python-version sessions. |
| `compatibility` | `dict[str, Any]` | Reserved for compatibility-matrix configuration; not yet consumed by the session engine. |
| `args` | `dict[str, list[str]]` | Adds arguments to a tool command, keyed by its Nox session name. |
| `env` | `dict[str, str]` | Reserved; not yet applied to tool sessions. |
| `exclude` | `list[dict[str, Any]]` | Reserved for matrix exclusions; not yet consumed by the session engine. |
| `skip_combination` | `Callable[[dict[str, Any]], bool] \| None` | Reserved for matrix filtering; not yet consumed by the session engine. |
| `dependencies` | `dict[str, list[str]]` | Adds package requirements for a tool session, keyed by session name. When set, this list overrides that tool's `Tool.dependencies`. |
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
| `command_prefix` | Replaces the default executable command. Its first item is checked for availability in the session environment. |
| `default_args` | Arguments appended after `command_prefix` and before any `Project.args` for the session. |
| `dependencies` | Additional package requirements installed into the session environment. |
| `description` | Description shown by Nox when listing sessions. |
| `dependency_group` | Installs a PEP 735 dependency group from the project with `uv`, instead of implicitly installing a package named after the tool. |

Every tool session installs the project editable (`-e .`) first. It then
installs `dependency_group`, if configured, and the applicable package
requirements. `Project.dependencies[session_name]` takes precedence over
`Tool.dependencies`; otherwise `Tool.dependencies` is used. If neither a
dependency group nor explicit dependencies are configured, NoxKit installs a
package matching the session name.

`Tool.get_command(args)` builds the final executable command as:

```text
command_prefix or (session_name,), default_args, args
```

The engine checks that the executable is available after installing the
dependencies and before starting the command.

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
