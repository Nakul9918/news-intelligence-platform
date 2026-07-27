from fastapi import HTTPException


class NewsNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="News article not found"
        )


class InvalidQueryException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Invalid request"
        )


class DatabaseException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=500,
            detail="Database error"
        )