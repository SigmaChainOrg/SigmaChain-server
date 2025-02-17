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
