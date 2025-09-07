class ResourceNotFoundException(Exception):
    """Exception raised when a requested resource is not found."""


class EntityNotFoundException(ResourceNotFoundException):
    """Exception raised when a requested entity is not found."""

    __slots__ = ("entity_id",)

    def __init__(self, entity_id: str) -> None:
        super().__init__(f"Entity with ID '{entity_id}' not found.")
        self.entity_id = entity_id
