# DevKit – Requirements

## 1. Overview

DevKit is a Python-configured developer command and workflow runner designed to simplify repetitive development tasks and automate common project workflows.

It provides a shorthand for frequently used commands, a way to combine commands into reusable workflows, and an extensible foundation for project validation and testing.

DevKit aims to provide a modern, Python-based alternative to shell aliases, Makefiles, and project-specific scripts, using Nox as its initial execution engine.

## 2. Core Features

### Command Definitions

- Define named commands using a simple Python configuration API.
- Execute commands through a short, consistent CLI.
- Support ordinary shell commands and executable arguments.
- Allow commands to accept and forward user-supplied arguments.
- Support working directories and environment variables.
- Provide a command listing and help output.

### Workflow Execution

- Execute multiple jobs sequentially or in parallel.
- Group jobs into ordered stages.
- Define dependencies between jobs.
- Support conditional execution and configurable failure behavior.
- Capture exit codes and execution results.
- Provide useful output and summaries, including failed commands.

### Execution Engine

- Use Nox as the initial execution and orchestration backend.
- Support commands that do not require a Python virtual environment.
- Reuse Nox's environment management where appropriate.
- Keep the public configuration API independent of Nox-specific implementation details.
- Leave room for alternative execution backends in the future.

## 3. Configuration

Support two configuration scopes:

**Project configuration**
- Commands and workflows specific to a repository.
- Project validation and testing configuration.
- Custom commands alongside built-in functionality.
- Configuration discoverable from the project directory.

**Global configuration**
- User-defined commands available across projects.
- Stored in a user-level configuration location.
- Support commands that operate independently of a project.
- Allow access to the current working directory and command arguments.

Configuration should favor simple Python objects and sensible defaults over extensive boilerplate.

## 4. Project Validation

Provide optional built-in workflows for common development checks.

Initial Python support:
- Ruff
- Pylint
- Bandit
- Pytest
- Coverage
- Python version compatibility testing.
- Framework compatibility matrices, initially targeting Django.

Future ecosystem integrations may include:
- JavaScript/TypeScript: ESLint, Prettier, TypeScript, Vitest/Jest.
- Rust: Clippy, rustfmt, Cargo test.
- Go: gofmt, golangci-lint, go test.

Language-specific integrations should build on the shared command and workflow engine rather than introduce separate execution systems.

## 5. Compatibility and Environment Management

- Work with system-installed Nox and Nox installed through common Python tooling such as uv and Poetry.
- Support existing project environments for ordinary project checks.
- Use isolated uv environments for Python compatibility matrix jobs.
- Do not unnecessarily replace or upgrade dependencies in existing project environments.
- Allow external tools such as Docker Compose, npm, pnpm, and Git to execute without requiring Python environments.

## 6. CLI

Provide a standalone `devkit` command.

Initial functionality:
- Run a named command or workflow.
- List available commands.
- Display command help.
- Forward arguments to configured commands.
- Report execution status and failures.
- Support running individual jobs where appropriate.

Example:

```bash
devkit --list
devkit up
devkit down
devkit logs
devkit rebuild
devkit test
devkit check
```

## 7. Reporting

- Preserve useful output from underlying commands.
- Report successful, failed, and skipped jobs.
- Include failure reasons and exit codes.
- Show commands that can be used to rerun failed jobs.
- Provide a final summary even when individual jobs fail.
- Support reporting for both individual commands and larger workflows.

## 8. Design Principles

- Simple, readable Python configuration.
- Sensible defaults with explicit overrides.
- Minimal required dependencies.
- KISS and DRY; avoid unnecessary abstraction.
- Prefer existing tools over reimplementing their functionality.
- Keep the core workflow engine separate from language-specific integrations.
- Avoid requiring users to learn Nox internals.
- Support custom commands without requiring changes to DevKit itself.

## 9. Initial Development Scope

The first release should focus on:

1. Basic Python configuration API.
2. Named command definitions.
3. Sequential and parallel job execution.
4. Ordered workflow stages.
5. Nox-based execution.
6. Basic CLI with command discovery and execution.
7. Project-local configuration.
8. Execution summaries and error reporting.
9. Initial Python linting and testing integrations.

Global configuration, compatibility matrices, additional language integrations, and alternative execution backends can follow once the core is established.

## 10. Definition of Success

A developer should be able to replace frequently typed shell commands, simple aliases, and basic Makefile workflows with a small Python configuration.

The same system should eventually support project validation, multi-step development workflows, and reusable global developer commands without becoming a complicated framework.