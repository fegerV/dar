from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(
            status_code=status_code,
            detail={"error": {"code": code, "message": message, "details": details or {}}},
        )


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", details: dict | None = None):
        super().__init__("NOT_FOUND", message, status.HTTP_404_NOT_FOUND, details)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Not authenticated", details: dict | None = None):
        super().__init__("UNAUTHORIZED", message, status.HTTP_401_UNAUTHORIZED, details)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden", details: dict | None = None):
        super().__init__("FORBIDDEN", message, status.HTTP_403_FORBIDDEN, details)


class ConflictException(AppException):
    def __init__(self, message: str = "Conflict", details: dict | None = None):
        super().__init__("CONFLICT", message, status.HTTP_409_CONFLICT, details)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation error", details: dict | None = None):
        super().__init__("VALIDATION_ERROR", message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)
