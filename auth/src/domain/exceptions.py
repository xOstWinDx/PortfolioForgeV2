class ConflictError(Exception):
    def __init__(self, message: str = "User already exists") -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return self.message


class AuthenticationError(Exception):
    def __init__(self, message: str = "Authentication error") -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return self.message


class AuthorizationError(Exception):
    def __init__(self, message: str = "Authorization error") -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return self.message


class ValidationError(Exception):
    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return self.message
