from noxkit.matrix.engine import MatrixEngine
from noxkit.project import Project


class NoxKitEngine:
    """Orchestrates the generation of Nox sessions."""
    
    def __init__(self, project: Project):
        self.project = project
        self.matrix_engine = MatrixEngine()

    def run(self) -> None:
        """
        1. Validate project.
        2. Generate matrix combinations if enabled.
        3. Generate Nox sessions for all checkers and tests.
        4. Execute and collect results.
        """
        raise NotImplementedError("Nox session generation is not implemented yet")