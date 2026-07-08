from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Contrato base de repositorio — implementaciones en infrastructure."""

    @abstractmethod
    def get_by_id(self, entity_id: str) -> T | None:
        raise NotImplementedError
