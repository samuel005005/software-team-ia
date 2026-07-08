from pathlib import Path


class WorkspaceError(Exception):
    """Error de validación o resolución de rutas dentro del workspace."""


class Workspace:
    """Espacio de trabajo acotado para operaciones seguras de filesystem."""

    def __init__(self, root_path: str) -> None:
        self._root = Path(root_path).expanduser().resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def resolve(self, path: str) -> Path:
        """Resuelve una ruta relativa validando que permanezca en el workspace."""
        if not isinstance(path, str) or not path.strip():
            raise WorkspaceError("La ruta es obligatoria")

        candidate = Path(path)
        if candidate.is_absolute():
            raise WorkspaceError("Las rutas absolutas no están permitidas")

        if ".." in candidate.parts:
            raise WorkspaceError("No se permiten rutas con '..'")

        target = (self._root / candidate).resolve()
        if not self._is_inside_workspace(target):
            raise WorkspaceError("La ruta está fuera del workspace")

        return target

    def exists(self, path: str) -> bool:
        try:
            return self.resolve(path).exists()
        except WorkspaceError:
            return False

    def absolute_path(self, path: str) -> Path:
        return self.resolve(path)

    def _is_inside_workspace(self, target: Path) -> bool:
        try:
            target.relative_to(self._root)
            return True
        except ValueError:
            return False
