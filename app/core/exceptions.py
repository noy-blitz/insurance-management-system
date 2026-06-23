class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""


class ConflictError(Exception):
    """Raised when an operation would violate a uniqueness or state constraint."""


class BusinessRuleError(Exception):
    """Raised when an operation violates a domain business rule (e.g. invalid date range)."""
