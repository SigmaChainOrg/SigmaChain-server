from fastapi.exceptions import HTTPException


class EmailAlreadyExistsError(HTTPException):
    """Exception when the email is already registered in the database."""

    def __init__(self, message: str = "Email already exists.") -> None:
        super().__init__(status_code=400, detail=message)

    pass


class DatabaseIntegrityError(HTTPException):
    """Exception when a database integrity error occurs."""

    def __init__(self, message: str = "Database integrity error.") -> None:
        super().__init__(status_code=500, detail=message)

    pass


class AuthenticationError(HTTPException):
    """Exception when an authentication error occurs."""

    def __init__(self, message: str = "Authentication error.") -> None:
        super().__init__(
            status_code=401,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    pass


class BadRequestError(HTTPException):
    """Exception when a bad request error occurs."""

    def __init__(self, message: str = "Bad request error.") -> None:
        super().__init__(status_code=400, detail=message)

    pass


class NotFoundError(HTTPException):
    """Exception when a resource is not found in the database."""

    def __init__(self, message: str = "Resource not found.") -> None:
        super().__init__(status_code=404, detail=message)

    pass
