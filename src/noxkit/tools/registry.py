from noxkit.tools import Tool

tools: dict[str, Tool] = {
    "ruff": Tool(
        "ruff",
        command_prefix=("ruff", "check"),
        description="Check code style, formatting, and common errors with Ruff.",
    ),
    "ruff-format": Tool(
        "ruff-format",
        command_prefix=("ruff", "format"),
        description="Format Python code with Ruff.",
    ),
    "pylint": Tool(
        "pylint",
        description="Analyze code for errors and code quality issues with Pylint.",
    ),
    "bandit": Tool(
        "bandit",
        default_args=("-r", "src"),
        description="Scan Python code for common security issues with Bandit.",
    ),
    "pytest": Tool("pytest", description="Run Pytest."),
    "pytest-cov": Tool(
        "pytest-cov",
        command_prefix=("pytest", "--cov"),
        description="Run Pytest with coverage.",
    ),
    "mypy": Tool("mypy", description="Check Python type annotations with Mypy."),
    "pyright": Tool(
        "pyright",
        description="Check Python type annotations with Pyright.",
    ),
}