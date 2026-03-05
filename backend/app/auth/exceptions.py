from fastapi import HTTPException, status


class PharmAlertException(HTTPException):
    """Base exception for PharmAlert."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class InteractionContraindicatedException(PharmAlertException):
    """Raised when a contraindicated interaction is detected."""

    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
        )


class MajorInteractionWarning(PharmAlertException):
    """Raised when a major interaction is detected."""

    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class AllergyConflictException(PharmAlertException):
    """Raised when a prescription conflicts with a known allergy."""

    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
        )


class UnauthorizedRoleException(PharmAlertException):
    """Raised when a user does not have the required role."""

    def __init__(self, required_role: str):
        super().__init__(
            detail=f"Role requis: {required_role}",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundException(PharmAlertException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            detail=f"{resource} non trouve(e): {identifier}",
            status_code=status.HTTP_404_NOT_FOUND,
        )
