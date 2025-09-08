class ResourceNotFoundException(Exception):
    """Exception raised when a requested resource is not found."""


class EntityNotFoundException(ResourceNotFoundException):
    """Exception raised when a requested entity is not found."""

    __slots__ = ("entity_type", "entity_id")

    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(f"{entity_type} with ID '{entity_id}' not found.")
        self.entity_type = entity_type
        self.entity_id = entity_id


class BadRequestException(Exception):
    """Exception raised when a request is semantically invalid (HTTP 400)."""

    __slots__ = ("detail",)

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class ConflictException(Exception):
    """Exception raised when a conflict occurs (HTTP 409)."""

    __slots__ = ("detail",)

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class DuplicateEntityException(ConflictException):
    """Exception raised when trying to create an entity that already exists."""

    __slots__ = ("entity_type", "field", "value")

    def __init__(self, entity_type: str, field: str, value: str) -> None:
        detail = f"{entity_type} with {field} '{value}' already exists"
        super().__init__(detail)
        self.entity_type = entity_type
        self.field = field
        self.value = value


class ForeignKeyViolationException(BadRequestException):
    """Exception raised when a foreign key constraint is violated."""

    __slots__ = ("field", "value", "referenced_entity")

    def __init__(self, field: str, value: str, referenced_entity: str | None = None) -> None:
        if referenced_entity:
            detail = f"Referenced {referenced_entity} '{value}' for field '{field}' does not exist"
        else:
            detail = f"Referenced entity '{value}' for field '{field}' does not exist"
        super().__init__(detail)
        self.field = field
        self.value = value
        self.referenced_entity = referenced_entity


class ConcurrentModificationException(ConflictException):
    """Exception raised when a concurrent modification conflict occurs."""

    __slots__ = ("entity_type", "entity_id")

    def __init__(self, entity_type: str, entity_id: str) -> None:
        detail = f"{entity_type} '{entity_id}' was modified by another process. Please retry with the latest data."
        super().__init__(detail)
        self.entity_type = entity_type
        self.entity_id = entity_id
