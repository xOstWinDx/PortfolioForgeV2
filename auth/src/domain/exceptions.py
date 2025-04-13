class ConflictError(Exception):
    def __init__(self, message: str = "User already exists") -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return self.message


class UnauthorizedError(Exception):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return self.message
