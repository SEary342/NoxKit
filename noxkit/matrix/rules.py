from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class CompatibilityRule:
    """A named predicate describing whether a matrix combination is valid."""

    name: str
    predicate: Callable[[dict[str, str]], bool]
    reason: str

    def allows(self, combination: dict[str, str]) -> bool:
        return self.predicate(combination)