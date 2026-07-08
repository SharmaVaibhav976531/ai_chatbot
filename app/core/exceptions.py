# backend/app/core/exceptions.py

from fastapi import HTTPException, status

class BaseAppException(Exception):
    """Base exception for the application."""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(BaseAppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class UnauthorizedException(BaseAppException):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

class ForbiddenException(BaseAppException):
    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)

class BadRequestException(BaseAppException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

class RateLimitException(BaseAppException):
    def __init__(self, message: str = "Too many requests"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)