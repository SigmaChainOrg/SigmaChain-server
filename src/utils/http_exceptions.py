from typing import List

from fastapi.exceptions import HTTPException


class EmailAlreadyExistsError(HTTPException):
    """Exception when the email is already registered in the database."""

    def __init__(self, message: str | List[str] = "Email already exists.") -> None:
        super().__init__(status_code=409, detail=message)


class DatabaseIntegrityError(HTTPException):
    """Exception when a database integrity error occurs."""

    def __init__(
        self,
        detail: str | List[str] = "Database integrity error.",
    ) -> None:
        super().__init__(status_code=500, detail=detail)


class AuthenticationError(HTTPException):
    """Exception when an authentication error occurs."""

    def __init__(
        self,
        detail: str | List[str] = "Authentication error.",
    ) -> None:
        super().__init__(
            status_code=401,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class BadRequestError(HTTPException):
    """Exception when a bad request error occurs."""

    def __init__(
        self,
        detail: str | List[str] = "Bad request error.",
    ) -> None:
        super().__init__(status_code=400, detail=detail)


class NotFoundError(HTTPException):
    """Exception when a resource is not found in the database."""

    def __init__(
        self,
        detail: str | List[str] = "Resource not found.",
    ) -> None:
        super().__init__(status_code=404, detail=detail)


class UnprocessableEntityError(HTTPException):
    """Exception when an unprocessable entity error occurs."""

    def __init__(
        self,
        detail: str | List[str] = "Unprocessable entity error.",
    ) -> None:
        super().__init__(status_code=422, detail=detail)


class InternalServerError(HTTPException):
    """Exception when an internal server error occurs."""

    def __init__(
        self,
        detail: str | List[str] = "Internal server error.",
    ) -> None:
        super().__init__(status_code=500, detail=detail)
